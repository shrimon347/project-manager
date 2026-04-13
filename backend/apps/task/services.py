from django.db import transaction
from django.utils import timezone

from apps.activity.models import ActivityAction, ActivityResourceType
from apps.activity.services import ActivityService
from core.exceptions import ForbiddenException, NotFoundException

from .models import SubTask, Task


class TaskService:
    """Application service for task workflows."""

    @staticmethod
    @transaction.atomic
    def create_task(*, user, project_id, **payload):
        """Create task in project for authorized member.

        Parameters:
        - user: authenticated user
        - project_id: target project UUID
        - payload: validated task fields

        Returns:
        - dict task payload
        """
        project = TaskService._authorized_project(user=user, project_id=project_id)
        assignee_ids = payload.pop("assignee_ids", [])
        task = Task.objects.create(project=project, created_by=user, **payload)
        if assignee_ids:
            assignees = list(project.workspace.members.filter(id__in=assignee_ids))
            task.assignees.set(assignees)
        ActivityService.record_activity(
            user=user,
            action=ActivityAction.TASK_CREATED,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"project_id": str(project.id), "title": task.title},
        )
        return TaskService.get_task_by_id(user=user, task_id=task.id)

    @staticmethod
    def get_task_by_id(*, user, task_id):
        """Get task details with assignees/watchers/project.

        Parameters:
        - user: authenticated user
        - task_id: task UUID

        Returns:
        - dict task payload
        """
        task = TaskService._authorized_task(user=user, task_id=task_id)
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def update_title(*, user, task_id, value):
        """Update task title.

        Parameters:
        - user: authenticated user
        - task_id: task UUID
        - value: new title

        Returns:
        - dict task payload
        """
        task = TaskService._authorized_task(user=user, task_id=task_id)
        task.title = value.strip()
        task.save(update_fields=["title", "updated_at"])
        TaskService._record_task_update(user=user, task=task, action=ActivityAction.TASK_UPDATED, details={"field": "title"})
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def update_description(*, user, task_id, value):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        task.description = value
        task.save(update_fields=["description", "updated_at"])
        TaskService._record_task_update(user=user, task=task, action=ActivityAction.TASK_UPDATED, details={"field": "description"})
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def update_status(*, user, task_id, value):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        task.status = value
        task.completed_at = timezone.now() if value == "Done" else None
        task.save(update_fields=["status", "completed_at", "updated_at"])
        TaskService._record_task_update(user=user, task=task, action=ActivityAction.TASK_STATUS_CHANGED, details={"status": value})
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def update_priority(*, user, task_id, value):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        task.priority = value
        task.save(update_fields=["priority", "updated_at"])
        TaskService._record_task_update(user=user, task=task, action=ActivityAction.TASK_PRIORITY_CHANGED, details={"priority": value})
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def update_assignees(*, user, task_id, value):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        assignees = task.project.workspace.members.filter(id__in=value)
        task.assignees.set(assignees)
        TaskService._record_task_update(
            user=user,
            task=task,
            action=ActivityAction.TASK_ASSIGNEES_CHANGED,
            details={"assignee_ids": [str(uid) for uid in value]},
        )
        return TaskService._task_payload(task)

    @staticmethod
    @transaction.atomic
    def add_subtask(*, user, task_id, title):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        subtask = SubTask.objects.create(task=task, title=title)
        ActivityService.record_activity(
            user=user,
            action=ActivityAction.SUBTASK_CREATED,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"subtask_id": str(subtask.id)},
        )
        return {"id": str(subtask.id), "title": subtask.title, "completed": subtask.completed, "created_at": subtask.created_at}

    @staticmethod
    @transaction.atomic
    def update_subtask(*, user, task_id, subtask_id, **payload):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        subtask = task.subtasks.filter(id=subtask_id).first()
        if not subtask:
            raise NotFoundException(detail="Subtask not found.", code="subtask_not_found")
        if "title" in payload:
            subtask.title = payload["title"]
        if "completed" in payload:
            subtask.completed = payload["completed"]
        subtask.save(update_fields=["title", "completed", "updated_at"])
        ActivityService.record_activity(
            user=user,
            action=ActivityAction.SUBTASK_UPDATED,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"subtask_id": str(subtask.id)},
        )
        return {"id": str(subtask.id), "title": subtask.title, "completed": subtask.completed, "created_at": subtask.created_at}

    @staticmethod
    @transaction.atomic
    def add_comment(*, user, task_id, **payload):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        from apps.comment.services import CommentService

        comment = CommentService.add_comment(user=user, task=task, **payload)
        ActivityService.record_activity(
            user=user,
            action=ActivityAction.COMMENT_ADDED,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"comment_id": str(comment["id"])},
        )
        return comment

    @staticmethod
    def get_comments(*, user, task_id):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        from apps.comment.services import CommentService

        return CommentService.get_comments(task=task)

    @staticmethod
    @transaction.atomic
    def toggle_watch(*, user, task_id):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        if task.watchers.filter(id=user.id).exists():
            task.watchers.remove(user)
            watched = False
            action = ActivityAction.WATCHER_REMOVED
        else:
            task.watchers.add(user)
            watched = True
            action = ActivityAction.WATCHER_ADDED
        ActivityService.record_activity(
            user=user,
            action=action,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"watched": watched},
        )
        return {"task_id": str(task.id), "watched": watched}

    @staticmethod
    @transaction.atomic
    def toggle_achieved(*, user, task_id):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        task.is_archived = not task.is_archived
        task.save(update_fields=["is_archived", "updated_at"])
        action = ActivityAction.TASK_ARCHIVED if task.is_archived else ActivityAction.TASK_UNARCHIVED
        ActivityService.record_activity(
            user=user,
            action=action,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details={"is_archived": task.is_archived},
        )
        return TaskService._task_payload(task)

    @staticmethod
    def get_my_tasks(*, user):
        tasks = Task.objects.filter(assignees=user).select_related("project").distinct().order_by("-created_at")
        return [TaskService._task_payload(task) for task in tasks]

    @staticmethod
    def get_task_activity(*, user, task_id):
        task = TaskService._authorized_task(user=user, task_id=task_id)
        logs = ActivityService.get_by_resource(resource_id=task.id)
        return [
            {
                "id": str(log.id),
                "user_id": str(log.user_id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id),
                "details": log.details,
                "created_at": log.created_at,
            }
            for log in logs
        ]

    @staticmethod
    def _task_payload(task):
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "project_id": str(task.project_id),
            "assignee_ids": [member.id for member in task.assignees.values_list("id", flat=True)],
            "watcher_ids": [member.id for member in task.watchers.values_list("id", flat=True)],
            "due_date": task.due_date,
            "completed_at": task.completed_at,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "tags": task.tags,
            "created_by": str(task.created_by_id),
            "is_archived": task.is_archived,
            "created_at": task.created_at,
        }

    @staticmethod
    def _authorized_project(*, user, project_id):
        from apps.project.models import Project
        from apps.workspaces.models import WorkspaceMember

        project = Project.objects.select_related("workspace").filter(id=project_id).first()
        if not project:
            raise NotFoundException(detail="Project not found.", code="project_not_found")
        if not WorkspaceMember.objects.filter(workspace=project.workspace, user=user).exists():
            raise ForbiddenException(detail="Project access denied.", code="project_access_denied")
        return project

    @staticmethod
    def _authorized_task(*, user, task_id):
        task = Task.objects.select_related("project", "project__workspace").filter(id=task_id).first()
        if not task:
            raise NotFoundException(detail="Task not found.", code="task_not_found")
        from apps.workspaces.models import WorkspaceMember

        if not WorkspaceMember.objects.filter(workspace=task.project.workspace, user=user).exists():
            raise ForbiddenException(detail="Task access denied.", code="task_access_denied")
        return task

    @staticmethod
    def _record_task_update(*, user, task, action, details):
        ActivityService.record_activity(
            user=user,
            action=action,
            resource_type=ActivityResourceType.TASK,
            resource_id=task.id,
            details=details,
        )
