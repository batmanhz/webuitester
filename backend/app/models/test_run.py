from tortoise import fields, models
import uuid

class TestRun(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    case = fields.ForeignKeyField("models.TestCase", related_name="runs")
    status = fields.CharField(max_length=50, default="PENDING")  # PENDING, RUNNING, PASSED, FAILED
    logs = fields.JSONField(default=list)
    result_summary = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "test_runs"
