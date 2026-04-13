from apps.comment.models import Comment


class CommentService:
    """Application service for task comments."""

    @staticmethod
    def add_comment(*, user, task, text, mentions=None, reactions=None, attachments=None):
        """Create comment for a task.

        Parameters:
        - user: authenticated user instance
        - task: task model instance
        - text: comment text
        - mentions: optional mention metadata
        - reactions: optional reactions metadata
        - attachments: optional attachment metadata

        Returns:
        - dict comment payload
        """
        comment = Comment.objects.create(
            text=text,
            task=task,
            author=user,
            mentions=mentions or [],
            reactions=reactions or [],
            attachments=attachments or [],
        )
        return CommentService._payload(comment)

    @staticmethod
    def get_comments(*, task):
        """Get comments by task.

        Parameters:
        - task: task model instance

        Returns:
        - list of comment payload dictionaries
        """
        return [CommentService._payload(item) for item in task.comments.all().order_by("created_at")]

    @staticmethod
    def _payload(comment):
        return {
            "id": str(comment.id),
            "text": comment.text,
            "task_id": str(comment.task_id),
            "author_id": str(comment.author_id),
            "mentions": comment.mentions,
            "reactions": comment.reactions,
            "attachments": comment.attachments,
            "is_edited": comment.is_edited,
            "created_at": comment.created_at,
        }
