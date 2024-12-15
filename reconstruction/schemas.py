from drf_yasg import openapi

work_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pk': openapi.Schema(type=openapi.TYPE_INTEGER),
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'price': openapi.Schema(type=openapi.TYPE_INTEGER),
        'imageurl': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

reconstruction_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pk': openapi.Schema(type=openapi.TYPE_INTEGER),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'creation_date': openapi.Schema(type=openapi.TYPE_STRING),
        'apply_date': openapi.Schema(type=openapi.TYPE_STRING),
        'end_date': openapi.Schema(type=openapi.TYPE_STRING),
        'creator': openapi.Schema(type=openapi.TYPE_STRING),
        'moderator': openapi.Schema(type=openapi.TYPE_INTEGER),
        'place': openapi.Schema(type=openapi.TYPE_STRING),
        'fundraising': openapi.Schema(type=openapi.TYPE_STRING),
    }
)