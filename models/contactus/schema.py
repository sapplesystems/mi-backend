from .serializer import CreateContactusSerializer


def create_contactus(application):
    serializer = CreateContactusSerializer(data=application)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data
