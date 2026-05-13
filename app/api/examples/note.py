note_examples = {
    "simple_note": {
        "summary": "Simple note",
        "value": {
            "title": "Shopping list",
            "content": "Milk, bread, eggs",
        },
    },
    "work_note": {
        "summary": "Work note",
        "value": {
            "title": "Sprint plan",
            "content": "Finish authentication, notes CRUD, and RabbitMQ integration",
        },
    },
    "idea_note": {
        "summary": "Project idea",
        "value": {
            "title": "New feature idea",
            "content": "Add tags for notes and filtering by tags",
        },
    },
}

note_responses = {
    200: {
        "description": "Successful response with a list of notes",
        "content": {
            "application/json": {
                "example": {
                    "items": [
                        {
                            "id": 1,
                            "title": "Shopping list",
                            "content": "Milk, bread, eggs",
                            "user_id": 1,
                            "is_archived": False,
                            "archived_at": None,
                            "created_at": "2026-05-14T02:30:00",
                            "updated_at": "2026-05-14T02:30:00",
                        },
                        {
                            "id": 2,
                            "title": "Sprint plan",
                            "content": "Finish authentication and notes CRUD",
                            "user_id": 1,
                            "is_archived": False,
                            "archived_at": None,
                            "created_at": "2026-05-14T02:35:00",
                            "updated_at": "2026-05-14T02:35:00",
                        },
                    ],
                    "limit": 20,
                    "offset": 0,
                    "total": 2,
                }
            }
        },
    }
}
