from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Project,
    ProjectInterest,
    ProjectCategory,
    ProjectTag,
    Milestone,
    MilestoneGoal,
    ProjectMentor,
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(ProjectTag)
class ProjectTagAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ProjectInterestInline(admin.TabularInline):
    model = ProjectInterest
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("wit", "old_user_id", "note", "created_at")


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        "title",
        "status",
        "difficulty",
        "get_owner",
        "get_assigned_wit",
        "funding_goal",
        "current_funding",
        "is_fully_funded",
        "created_at",
    )
    list_filter = ("status", "difficulty", "category", "tags", "created_at")
    search_fields = ("title", "description", "technologies")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProjectInterestInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "description", "image", "category", "tags")},
        ),
        (
            "Project Details",
            {
                "fields": (
                    "repo_link",
                    "deploy_link",
                    "technologies",
                    "difficulty",
                    "status",
                )
            },
        ),
        ("Funding Information", {"fields": ("funding_goal", "current_funding")}),
        (
            "Ownership",
            {
                "fields": (
                    "owner",
                    "old_owner_id",
                    "assigned_wit",
                    "old_assigned_wit_id",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def is_fully_funded(self, obj):
        return obj.is_fully_funded()

    is_fully_funded.boolean = True
    is_fully_funded.short_description = "Fully Funded"

    def get_owner(self, obj):
        if obj.owner:
            return f"{obj.owner.user.username}"
        elif obj.old_owner_id:
            return f"ID: {obj.old_owner_id}"
        return "-"

    get_owner.short_description = "Owner"

    def get_assigned_wit(self, obj):
        if obj.assigned_wit:
            return f"{obj.assigned_wit.user.username}"
        elif obj.old_assigned_wit_id:
            return f"ID: {obj.old_assigned_wit_id}"
        return "-"

    get_assigned_wit.short_description = "Assigned WIT"


@admin.register(ProjectInterest)
class ProjectInterestAdmin(ModelAdmin):
    list_display = ("project", "get_wit_display", "created_at")
    list_filter = ("created_at",)
    search_fields = ("project__title", "note", "wit__user__username")
    readonly_fields = ("created_at",)

    def get_wit_display(self, obj):
        if obj.wit:
            return f"{obj.wit.user.username}"
        elif obj.old_user_id:
            return f"User ID: {obj.old_user_id}"
        return "-"

    get_wit_display.short_description = "Woman in Tech"


@admin.register(Milestone)
class MilestoneAdmin(ModelAdmin):
    list_display = (
        "title",
        "project",
        "target_date",
        "completion_percentage",
        "locked",
    )
    list_filter = ("locked", "target_date", "project")
    search_fields = ("title", "description", "project__title")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "target_date"


class MilestoneGoalInline(admin.TabularInline):
    model = MilestoneGoal
    extra = 1
    readonly_fields = ("created_at", "updated_at")


@admin.register(MilestoneGoal)
class MilestoneGoalAdmin(ModelAdmin):
    list_display = ("title", "milestone", "status", "updated_at")
    list_filter = ("status", "milestone__project")
    search_fields = ("title", "description", "milestone__title")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProjectMentor)
class ProjectMentorAdmin(ModelAdmin):
    list_display = ("mentor", "project", "expertise_areas", "created_at")
    list_filter = ("project", "mentor")
    search_fields = ("project__title", "mentor__user__username", "expertise_areas")
    readonly_fields = ("created_at",)
