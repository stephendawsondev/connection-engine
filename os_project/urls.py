from django.urls import path
from . import views

urlpatterns = [
    # List and detail views
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("create/", views.ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/update/", views.ProjectUpdateView.as_view(), name="project_update"),
    path("<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project_delete"),
    # Interest management
    path(
        "<int:project_id>/express-interest/",
        views.express_interest,
        name="express_interest",
    ),
    path(
        "<int:project_id>/withdraw-interest/",
        views.withdraw_interest,
        name="withdraw_interest",
    ),
    # Project owner dashboard
    path("dashboard/", views.project_dashboard, name="project_dashboard"),
    path(
        "<int:project_id>/interested-users/",
        views.project_interested_users,
        name="project_interested_users",
    ),
    path(
        "<int:project_id>/select-wit/<int:interest_id>/",
        views.select_wit,
        name="select_wit",
    ),
    path(
        "<int:project_id>/toggle-favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path("<int:project_id>/milestones/", views.milestone_list, name="milestone_list"),
    path(
        "<int:project_id>/milestones/create/",
        views.milestone_create,
        name="milestone_create",
    ),
    path(
        "<int:project_id>/milestones/<int:milestone_id>/",
        views.milestone_detail,
        name="milestone_detail",
    ),
    path(
        "<int:project_id>/milestones/<int:milestone_id>/update/",
        views.milestone_update,
        name="milestone_update",
    ),
    path(
        "<int:project_id>/milestones/<int:milestone_id>/delete/",
        views.milestone_delete,
        name="milestone_delete",
    ),
    path(
        "<int:project_id>/milestones/<int:milestone_id>/lock/",
        views.lock_milestone,
        name="lock_milestone",
    ),
    path(
        "<int:project_id>/goals/<int:goal_id>/update-status/",
        views.update_goal_status,
        name="update_goal_status",
    ),
    path(
        "<int:project_id>/goals/<int:goal_id>/delete/",
        views.delete_goal,
        name="delete_goal",
    ),
    path("<int:project_id>/mentors/", views.manage_mentors, name="manage_mentors"),
    path(
        "<int:project_id>/mentors/<int:mentor_id>/remove/",
        views.remove_mentor,
        name="remove_mentor",
    ),
]
