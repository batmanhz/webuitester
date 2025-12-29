from tortoise import fields, models
import uuid

class TestCase(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    url = fields.CharField(max_length=2048)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    steps: fields.ReverseRelation["TestStep"]
    runs: fields.ReverseRelation["TestRun"]

    class Meta:
        table = "test_cases"

class TestStep(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    case = fields.ForeignKeyField("models.TestCase", related_name="steps")
    order = fields.IntField()
    instruction = fields.TextField()
    expected_result = fields.TextField(null=True)

    class Meta:
        table = "test_steps"
