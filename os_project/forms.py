from django import forms
from .models import (
    Project,
    ProjectInterest,
    ProjectCategory,
    ProjectTag,
    Milestone,
    MilestoneGoal,
    ProjectMentor,
)
from user_profile.models import Mentor


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects"""

    tags = forms.ModelMultipleChoiceField(
        queryset=ProjectTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "repo_link",
            "deploy_link",
            "image",
            "status",
            "difficulty",
            "funding_goal",
            "category",
            "tags",
            "technologies",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "technologies": forms.TextInput(
                attrs={"placeholder": "e.g., Python, Django, React"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop("user_id", None)
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "Select a category"


class ProjectInterestForm(forms.ModelForm):
    """Form for expressing interest in a project"""

    class Meta:
        model = ProjectInterest
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Explain why you are interested in this project and what skills you bring",
                }
            )
        }


class ProjectSearchForm(forms.Form):
    """Form for searching and filtering projects"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search project by title or description...",
                "class": "input input-bordered w-full mb-2",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=ProjectCategory.objects.all(),
        required=False,
        empty_label="All Categories",
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=ProjectTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    status = forms.ChoiceField(
        choices=[("", "All Status")] + list(Project.STATUS_CHOICES), required=False
    )
    difficulty = forms.ChoiceField(
        choices=[("", "All Difficulty Levels")] + list(Project.DIFFICULTY_CHOICES),
        required=False,
    )


class MilestoneForm(forms.ModelForm):
    """Form for creating and updating milestones"""

    class Meta:
        model = Milestone
        fields = ["title", "description", "target_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.project:
            instance.project = self.project
        if commit:
            instance.save()
        return instance


class MilestoneGoalForm(forms.ModelForm):
    """Form for creating and updating milestone goals"""

    class Meta:
        model = MilestoneGoal
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.milestone = kwargs.pop("milestone", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.milestone:
            instance.milestone = self.milestone
        if commit:
            instance.save()
        return instance


class MilestoneGoalUpdateForm(forms.ModelForm):
    """Form for updating milestone goal status"""

    class Meta:
        model = MilestoneGoal
        fields = ["status", "evidence_link", "evidence_image"]
        widgets = {
            "evidence_link": forms.URLInput(attrs={"placeholder": "https://..."}),
        }


class ProjectMentorForm(forms.ModelForm):
    """Form for adding mentors to projects"""

    class Meta:
        model = ProjectMentor
        fields = ["mentor", "expertise_areas", "availability", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        # Filter mentors who aren't already assigned to this project
        if self.project:
            existing_mentors = ProjectMentor.objects.filter(
                project=self.project
            ).values_list("mentor_id", flat=True)
            self.fields["mentor"].queryset = Mentor.objects.exclude(
                id__in=existing_mentors
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.project:
            instance.project = self.project
        if commit:
            instance.save()
        return instance
