from django import forms
from .models import Project, ProjectInterest, ProjectCategory, ProjectTag


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
