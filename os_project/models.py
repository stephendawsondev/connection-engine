from django.db import models
from cloudinary.models import CloudinaryField
from donations.models import Payment


class ProjectCategory(models.Model):
    """Categories for organizing projects"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Project categories"


class ProjectTag(models.Model):
    """Tags for filtering and organizing projects"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open for Interest"),
        ("ASSIGNED", "WIT Assigned"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    ]

    DIFFICULTY_CHOICES = [
        ("BEGINNER", "Beginner Friendly"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    repo_link = models.URLField()
    deploy_link = models.URLField(blank=True, null=True)
    image = CloudinaryField("image", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        "user_profile.OS_Maintainer",
        on_delete=models.CASCADE,
        related_name="owned_projects",
        null=True,
        blank=True,
    )
    old_owner_id = models.IntegerField(null=True, blank=True)

    assigned_wit = models.ForeignKey(
        "user_profile.WomenInTech",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_projects",
    )
    # Keep old_assigned_wit_id for backward compatibility during migration
    old_assigned_wit_id = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    difficulty = models.CharField(
        max_length=15, choices=DIFFICULTY_CHOICES, default="INTERMEDIATE"
    )

    # Funding information
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2)
    current_funding = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Categories and tags
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL, null=True, related_name="projects"
    )
    tags = models.ManyToManyField(ProjectTag, blank=True, related_name="projects")

    # For storing technologies used
    technologies = models.CharField(
        max_length=500, blank=True, help_text="Comma-separated list of technologies"
    )

    def __str__(self):
        return self.title

    def is_fully_funded(self):
        return self.current_funding >= self.funding_goal

    def funding_percentage(self):
        if self.funding_goal <= 0:
            return 0
        return min(100, int((self.current_funding / self.funding_goal) * 100))

    def get_technologies_list(self):
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(",")]
        return []

    def update_funding(self):
        """
        Update the current_funding value based on actual payments/donations
        received through Stripe.
        """

        # Get all successful payments related to this project
        successful_payments = Payment.objects.filter(project=self, status="SUCCESS")

        # Calculate total funding
        total_funding = (
            successful_payments.aggregate(total=models.Sum("amount"))["total"] or 0
        )

        # Update the current_funding field
        self.current_funding = total_funding
        self.save(update_fields=["current_funding"])

        return self.current_funding


class ProjectInterest(models.Model):
    """Track Women in Tech who are interested in a project"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="interested_users"
    )
    wit = models.ForeignKey(
        "user_profile.WomenInTech",
        on_delete=models.CASCADE,
        related_name="project_interests",
        null=True,
        blank=True,
    )
    # Keep for backward compatibility
    old_user_id = models.IntegerField(null=True, blank=True)

    note = models.TextField(
        blank=True, help_text="Why are you interested in this project?"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "wit")

    def __str__(self):
        if self.wit:
            return f"Interest in {self.project.title} by {self.wit.user.username}"
        return f"Interest in {self.project.title} (User: {self.old_user_id})"
