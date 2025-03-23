from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .models import Project, ProjectInterest, Milestone, MilestoneGoal, ProjectMentor
from .forms import (
    ProjectForm,
    ProjectInterestForm,
    ProjectSearchForm,
    MilestoneForm,
    MilestoneGoalForm,
    MilestoneGoalUpdateForm,
    ProjectMentorForm,
)
from user_profile.models import OS_Maintainer, WomenInTech, FavouriteProject
from .decorators import os_maintainer_required, OSMaintainerRequiredMixin

from django.conf import settings


class ProjectListView(ListView):
    model = Project
    template_name = "os_project/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ProjectSearchForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get("search")
            category = form.cleaned_data.get("category")
            tags = form.cleaned_data.get("tags")
            status = form.cleaned_data.get("status")
            difficulty = form.cleaned_data.get("difficulty")

            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search)
                    | Q(description__icontains=search)
                    | Q(technologies__icontains=search)
                )

            if category:
                queryset = queryset.filter(category=category)

            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()

            if status:
                queryset = queryset.filter(status=status)

            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ProjectSearchForm(self.request.GET)
        return context


class ProjectDetailView(DetailView):
    """
    View for displaying the project's page
    """

    model = Project
    template_name = "os_project/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the latest funding amount
        self.object.update_funding()

        # Check if the user has already expressed interest in this project
        user_interested = False
        is_favorited = False

        if self.request.user.is_authenticated:
            # Check if user is a Women in Tech
            try:
                wit_profile = WomenInTech.objects.get(user=self.request.user)
                user_interested = ProjectInterest.objects.filter(
                    project=self.object, wit=wit_profile
                ).exists()
            except WomenInTech.DoesNotExist:
                # Fallback to legacy check based on old_user_id
                user_interested = ProjectInterest.objects.filter(
                    project=self.object, old_user_id=self.request.user.id
                ).exists()

            # Check if user has favorited this project using the Profile model
            is_favorited = FavouriteProject.objects.filter(
                profile=self.request.user.profile, project=self.object
            ).exists()

            context["user_interested"] = user_interested
            context["is_favorited"] = is_favorited
            context["interest_form"] = ProjectInterestForm()

            # Get all users who have expressed interest
            context["interest_count"] = ProjectInterest.objects.filter(
                project=self.object
            ).count()

            # Check if user is the owner
            if self.request.user.is_authenticated:
                try:
                    osm_profile = OS_Maintainer.objects.get(user=self.request.user)
                    context["is_owner"] = self.object.owner == osm_profile
                except OS_Maintainer.DoesNotExist:
                    # Fallback to legacy check
                    context["is_owner"] = (
                        self.object.old_owner_id == self.request.user.id
                    )

            # Check if user is a mentor for this project
            context["is_mentor"] = ProjectMentor.objects.filter(
                project=self.object, mentor__user=self.request.user
            ).exists()

            # Check if user is the assigned WIT
            context["is_assigned_wit"] = check_assigned_wit(
                self.request.user, self.object
            )

            context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY

            # Add donation information
            from donations.models import Payment

            context["recent_donations"] = Payment.objects.filter(
                project=self.object, status="SUCCESS"
            ).order_by("-created_at")[:5]

            # Add milestone information
            context["milestones"] = Milestone.objects.filter(
                project=self.object
            ).order_by("target_date")

            # Get project mentors
            context["project_mentors"] = ProjectMentor.objects.filter(
                project=self.object
            )

        return context


# Create, Update, Delete views
class ProjectCreateView(OSMaintainerRequiredMixin, LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "os_project/project_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def form_valid(self, form):
        # Check if user is an OS Maintainer and set the owner
        try:
            osm_profile = OS_Maintainer.objects.get(user=self.request.user)
            form.instance.owner = osm_profile
        except OS_Maintainer.DoesNotExist:
            # Fallback to setting just the old_owner_id
            form.instance.old_owner_id = self.request.user.id

        messages.success(self.request, "Project created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(OSMaintainerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "os_project/project_form.html"

    def get_queryset(self):
        # Get projects owned by current user (check both owner and old_owner_id)
        user = self.request.user
        queryset = Project.objects.all()

        try:
            osm_profile = OS_Maintainer.objects.get(user=user)
            return queryset.filter(Q(owner=osm_profile) | Q(old_owner_id=user.id))
        except OS_Maintainer.DoesNotExist:
            return queryset.filter(old_owner_id=user.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project_detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(OSMaintainerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "os_project/project_confirm_delete.html"
    success_url = reverse_lazy("project_list")

    def get_queryset(self):
        # Get projects owned by current user (check both owner and old_owner_id)
        user = self.request.user
        queryset = Project.objects.all()

        try:
            osm_profile = OS_Maintainer.objects.get(user=user)
            return queryset.filter(Q(owner=osm_profile) | Q(old_owner_id=user.id))
        except OS_Maintainer.DoesNotExist:
            return queryset.filter(old_owner_id=user.id)

    def delete(self, request, *args, **kwargs):
        project = self.get_object()

        # Check if a WIT is assigned to this project
        if project.assigned_wit is not None or project.old_assigned_wit_id is not None:
            messages.error(
                request,
                "Cannot delete a project that has a Woman in Tech assigned to it.",
            )
            return redirect("project_detail", pk=project.pk)

        messages.success(request, "Project deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Project Interest
@login_required
def express_interest(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    # Check if user is a WomenInTech
    try:
        wit_profile = WomenInTech.objects.get(user=user)
    except WomenInTech.DoesNotExist:
        messages.error(
            request, "Only Women in Tech can express interest in joining a project."
        )
        return redirect("project_detail", pk=project_id)

    # Check if user has already expressed interest
    existing_interest = ProjectInterest.objects.filter(
        project=project, wit=wit_profile
    ).exists()

    if existing_interest:
        messages.info(request, "You have already expressed interest in this project")
        return redirect("project_detail", pk=project_id)

    if request.method == "POST":
        form = ProjectInterestForm(request.POST)
        if form.is_valid():
            interest = form.save(commit=False)
            interest.project = project
            interest.wit = wit_profile
            interest.old_user_id = user.id  # Keep for backward compatibility
            interest.save()

            messages.success(request, "Your interest has been recorded")
            return redirect("project_detail", pk=project_id)
    else:
        form = ProjectInterestForm()

    return render(
        request, "os_project/express_interest.html", {"form": form, "project": project}
    )


@login_required
def withdraw_interest(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    # Find interest based on WIT profile or old_user_id
    interest = None
    try:
        wit_profile = WomenInTech.objects.get(user=user)
        interest = ProjectInterest.objects.filter(
            project=project, wit=wit_profile
        ).first()
    except WomenInTech.DoesNotExist:
        # Fallback to legacy old_user_id
        interest = ProjectInterest.objects.filter(
            project=project, old_user_id=user.id
        ).first()

    if interest:
        interest.delete()
        messages.success(request, "Your interest has been withdrawn")
    else:
        messages.error(request, "You have not expressed interest in this project")

    return redirect("project_detail", pk=project_id)


# Dashboard views for project owners
@login_required
@os_maintainer_required
def project_dashboard(request):
    user = request.user

    # Get projects owned by the current user
    try:
        osm_profile = OS_Maintainer.objects.get(user=user)
        owned_projects = Project.objects.filter(
            Q(owner=osm_profile) | Q(old_owner_id=user.id)
        )
    except OS_Maintainer.DoesNotExist:
        # Fallback to just checking old_owner_id
        owned_projects = Project.objects.filter(old_owner_id=user.id)

    # Update funding for all owned projects
    for project in owned_projects:
        project.update_funding()

    return render(
        request, "os_project/project_dashboard.html", {"owned_projects": owned_projects}
    )


@login_required
@os_maintainer_required
def project_interested_users(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    # Check if user is the owner
    is_owner = False
    try:
        osm_profile = OS_Maintainer.objects.get(user=user)
        is_owner = project.owner == osm_profile
    except OS_Maintainer.DoesNotExist:
        pass

    # Fallback to legacy check
    if not is_owner:
        is_owner = project.old_owner_id == user.id

    if not is_owner:
        messages.error(request, "You are not authorized to view this page")
        return redirect("project_list")

    interested_users = ProjectInterest.objects.filter(project=project)

    return render(
        request,
        "os_project/project_interested_users.html",
        {"project": project, "interested_users": interested_users},
    )


@login_required
@os_maintainer_required
def select_wit(request, project_id, interest_id):
    project = get_object_or_404(Project, pk=project_id)
    interest = get_object_or_404(ProjectInterest, pk=interest_id, project=project)
    user = request.user

    # Check if user is the owner
    is_owner = False
    try:
        osm_profile = OS_Maintainer.objects.get(user=user)
        is_owner = project.owner == osm_profile
    except OS_Maintainer.DoesNotExist:
        pass

    # Fallback to legacy check
    if not is_owner:
        is_owner = project.old_owner_id == user.id

    if not is_owner:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("project_list")

    # Check if a WIT is already assigned
    if project.assigned_wit is not None or project.old_assigned_wit_id is not None:
        messages.error(request, "A Woman in Tech is already assigned to this project")
        return redirect("project_detail", pk=project_id)

    # Assign the WIT - use both new and legacy fields
    project.assigned_wit = interest.wit
    project.old_assigned_wit_id = interest.old_user_id
    project.status = "ASSIGNED"
    project.save()

    messages.success(request, "Woman in Tech has been assigned to the project")
    return redirect("project_detail", pk=project_id)


@login_required
def toggle_favorite(request, project_id):
    """Toggle favorite status of a project for the current user"""
    project = get_object_or_404(Project, pk=project_id)
    profile = request.user.profile
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    # Check if already favorited
    favorite = FavouriteProject.objects.filter(profile=profile, project=project).first()
    if favorite:
        # Remove from favorites
        favorite.delete()
        is_favorited = False
        message = "Project removed from favorites"
    else:
        # Add to favorites
        FavouriteProject.objects.create(profile=profile, project=project)
        is_favorited = True
        message = "Project added to favorites"

    if is_ajax:
        return JsonResponse(
            {"success": True, "is_favorited": is_favorited, "message": message}
        )

    messages.success(request, message)
    return redirect("project_detail", pk=project_id)


@login_required
@os_maintainer_required
def milestone_list(request, project_id):
    """View all milestones for a project"""
    project = get_object_or_404(Project, pk=project_id)

    # Check if user is the owner or a mentor
    is_owner = check_project_ownership(request.user, project)
    is_mentor = ProjectMentor.objects.filter(
        project=project, mentor__user=request.user
    ).exists()

    if not (is_owner or is_mentor):
        messages.error(
            request, "You don't have permission to view this project's milestones"
        )
        return redirect("project_detail", pk=project_id)

    milestones = Milestone.objects.filter(project=project).order_by("target_date")

    return render(
        request,
        "os_project/milestone_list.html",
        {
            "project": project,
            "milestones": milestones,
            "is_owner": is_owner,
            "is_mentor": is_mentor,
        },
    )


@login_required
@os_maintainer_required
def milestone_create(request, project_id):
    """Create a new milestone for a project"""
    project = get_object_or_404(Project, pk=project_id)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can create milestones")
        return redirect("project_detail", pk=project_id)

    if request.method == "POST":
        form = MilestoneForm(request.POST, project=project)
        if form.is_valid():
            milestone = form.save()
            messages.success(request, "Milestone created successfully!")
            return redirect(
                "milestone_detail", project_id=project_id, milestone_id=milestone.id
            )
    else:
        form = MilestoneForm(project=project)

    return render(
        request,
        "os_project/milestone_form.html",
        {
            "form": form,
            "project": project,
            "is_new": True,
        },
    )


@login_required
def milestone_detail(request, project_id, milestone_id):
    """View a milestone's details and goals"""
    project = get_object_or_404(Project, pk=project_id)
    milestone = get_object_or_404(Milestone, pk=milestone_id, project=project)

    # Check if user is the owner, a mentor, or the assigned WIT
    is_owner = check_project_ownership(request.user, project)
    is_mentor = ProjectMentor.objects.filter(
        project=project, mentor__user=request.user
    ).exists()
    is_assigned_wit = check_assigned_wit(request.user, project)

    if not (is_owner or is_mentor or is_assigned_wit):
        messages.error(request, "You don't have permission to view this milestone")
        return redirect("project_detail", pk=project_id)

    goals = MilestoneGoal.objects.filter(milestone=milestone).order_by("created_at")

    # Form for adding new goals (only for project owner)
    goal_form = None
    if is_owner and not milestone.locked:
        if request.method == "POST" and "add_goal" in request.POST:
            goal_form = MilestoneGoalForm(request.POST, milestone=milestone)
            if goal_form.is_valid():
                goal_form.save()
                messages.success(request, "Goal added successfully!")
                return redirect(
                    "milestone_detail", project_id=project_id, milestone_id=milestone_id
                )
        else:
            goal_form = MilestoneGoalForm(milestone=milestone)

    return render(
        request,
        "os_project/milestone_detail.html",
        {
            "project": project,
            "milestone": milestone,
            "goals": goals,
            "is_owner": is_owner,
            "is_mentor": is_mentor,
            "is_assigned_wit": is_assigned_wit,
            "goal_form": goal_form,
        },
    )


@login_required
@os_maintainer_required
def milestone_update(request, project_id, milestone_id):
    """Update a milestone"""
    project = get_object_or_404(Project, pk=project_id)
    milestone = get_object_or_404(Milestone, pk=milestone_id, project=project)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can update milestones")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    # Check if milestone is locked
    if milestone.locked:
        messages.error(request, "This milestone is locked and cannot be edited")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    if request.method == "POST":
        form = MilestoneForm(request.POST, instance=milestone, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Milestone updated successfully!")
            return redirect(
                "milestone_detail", project_id=project_id, milestone_id=milestone_id
            )
    else:
        form = MilestoneForm(instance=milestone, project=project)

    return render(
        request,
        "os_project/milestone_form.html",
        {
            "form": form,
            "project": project,
            "milestone": milestone,
            "is_new": False,
        },
    )


@login_required
@os_maintainer_required
def milestone_delete(request, project_id, milestone_id):
    """Delete a milestone"""
    project = get_object_or_404(Project, pk=project_id)
    milestone = get_object_or_404(Milestone, pk=milestone_id, project=project)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can delete milestones")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    # Check if milestone is locked
    if milestone.locked:
        messages.error(request, "This milestone is locked and cannot be deleted")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    if request.method == "POST":
        milestone.delete()
        messages.success(request, "Milestone deleted successfully!")
        return redirect("milestone_list", project_id=project_id)

    return render(
        request,
        "os_project/milestone_confirm_delete.html",
        {
            "project": project,
            "milestone": milestone,
        },
    )


@login_required
@os_maintainer_required
def lock_milestone(request, project_id, milestone_id):
    """Lock a milestone to prevent further edits"""
    project = get_object_or_404(Project, pk=project_id)
    milestone = get_object_or_404(Milestone, pk=milestone_id, project=project)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can lock milestones")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    if request.method == "POST":
        milestone.locked = True
        milestone.save()
        messages.success(request, "Milestone locked successfully!")

    return redirect(
        "milestone_detail", project_id=project_id, milestone_id=milestone_id
    )


# Goal Views
@login_required
def update_goal_status(request, project_id, goal_id):
    """Update a goal's status"""
    project = get_object_or_404(Project, pk=project_id)
    goal = get_object_or_404(MilestoneGoal, pk=goal_id, milestone__project=project)

    # Check permissions based on the action
    is_owner = check_project_ownership(request.user, project)
    is_mentor = ProjectMentor.objects.filter(
        project=project, mentor__user=request.user
    ).exists()
    is_assigned_wit = check_assigned_wit(request.user, project)

    # WIT can only mark as ready for review and provide evidence
    # Owners and mentors can mark as completed
    if not (is_owner or is_mentor or is_assigned_wit):
        messages.error(request, "You don't have permission to update this goal")
        return redirect("project_detail", pk=project_id)

    if request.method == "POST":
        form = MilestoneGoalUpdateForm(request.POST, request.FILES, instance=goal)
        if form.is_valid():
            updated_goal = form.save(commit=False)

            # Check permissions for specific status changes
            new_status = form.cleaned_data["status"]
            if new_status == "COMPLETED" and not (is_owner or is_mentor):
                messages.error(
                    request,
                    "Only project owners or mentors can mark goals as completed",
                )
                return redirect(
                    "milestone_detail",
                    project_id=project_id,
                    milestone_id=goal.milestone.id,
                )

            # WIT can only change to READY_FOR_REVIEW or IN_PROGRESS
            if is_assigned_wit and not (is_owner or is_mentor):
                if new_status not in ["IN_PROGRESS", "READY_FOR_REVIEW"]:
                    messages.error(
                        request,
                        "You can only mark goals as in progress or ready for review",
                    )
                    return redirect(
                        "milestone_detail",
                        project_id=project_id,
                        milestone_id=goal.milestone.id,
                    )

            updated_goal.save()
            messages.success(
                request, f"Goal status updated to {updated_goal.get_status_display()}"
            )
        else:
            messages.error(request, "There was an error updating the goal status")

    return redirect(
        "milestone_detail", project_id=project_id, milestone_id=goal.milestone.id
    )


@login_required
@os_maintainer_required
def delete_goal(request, project_id, goal_id):
    """Delete a goal"""
    project = get_object_or_404(Project, pk=project_id)
    goal = get_object_or_404(MilestoneGoal, pk=goal_id, milestone__project=project)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can delete goals")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=goal.milestone.id
        )

    # Check if milestone is locked
    if goal.milestone.locked:
        messages.error(request, "This milestone is locked and goals cannot be deleted")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=goal.milestone.id
        )

    if request.method == "POST":
        milestone_id = goal.milestone.id
        goal.delete()
        messages.success(request, "Goal deleted successfully!")
        return redirect(
            "milestone_detail", project_id=project_id, milestone_id=milestone_id
        )

    return render(
        request,
        "os_project/goal_confirm_delete.html",
        {
            "project": project,
            "goal": goal,
        },
    )


# Mentor views
@login_required
@os_maintainer_required
def manage_mentors(request, project_id):
    """Manage mentors for a project"""
    project = get_object_or_404(Project, pk=project_id)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can manage mentors")
        return redirect("project_detail", pk=project_id)

    mentors = ProjectMentor.objects.filter(project=project)

    if request.method == "POST":
        form = ProjectMentorForm(request.POST, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Mentor added successfully!")
            return redirect("manage_mentors", project_id=project_id)
    else:
        form = ProjectMentorForm(project=project)

    return render(
        request,
        "os_project/manage_mentors.html",
        {
            "project": project,
            "mentors": mentors,
            "form": form,
        },
    )


@login_required
@os_maintainer_required
def remove_mentor(request, project_id, mentor_id):
    """Remove a mentor from a project"""
    project = get_object_or_404(Project, pk=project_id)
    mentor_relation = get_object_or_404(ProjectMentor, pk=mentor_id, project=project)

    # Check if user is the owner
    if not check_project_ownership(request.user, project):
        messages.error(request, "Only the project owner can remove mentors")
        return redirect("manage_mentors", project_id=project_id)

    if request.method == "POST":
        mentor_relation.delete()
        messages.success(request, "Mentor removed successfully!")

    return redirect("manage_mentors", project_id=project_id)


# Helper functions
def check_project_ownership(user, project):
    """Check if the user is the owner of the project"""
    try:
        osm_profile = OS_Maintainer.objects.get(user=user)
        return project.owner == osm_profile or project.old_owner_id == user.id
    except OS_Maintainer.DoesNotExist:
        return project.old_owner_id == user.id


def check_assigned_wit(user, project):
    """Check if the user is the assigned WIT for the project"""
    try:
        wit_profile = WomenInTech.objects.get(user=user)
        return (
            project.assigned_wit == wit_profile
            or project.old_assigned_wit_id == user.id
        )
    except WomenInTech.DoesNotExist:
        return project.old_assigned_wit_id == user.id
