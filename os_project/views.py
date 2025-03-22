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

from .models import Project, ProjectInterest
from .forms import ProjectForm, ProjectInterestForm, ProjectSearchForm
from user_profile.models import OS_Maintainer, WomenInTech, FavouriteProject
from .decorators import os_maintainer_required, OSMaintainerRequiredMixin


# List views
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
    model = Project
    template_name = "os_project/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        messages.error(request, "Only Women in Tech can express interest in projects.")
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
