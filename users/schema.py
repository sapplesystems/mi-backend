import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from users.models import User


# return if user exists with given email
def get_user(email):
    return User.objects.filter(email=email).first()


def get_user_email(user_id):
    return User.objects.filter(id=user_id).values('username').first()


def get_user_id(email):
    return User.objects.filter(email=email).values('id').first()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude_fields = ['password']


class Query(graphene.ObjectType):
    user = graphene.Field(
        UserType,
        description='Return Current User\'s Information'
    )
    all_users = graphene.List(UserType, description='Return all Users')

    @login_required
    def resolve_user(self, info):
        return info.context.user

    @login_required
    def resolve_all_users(self, info):
        return User.objects.all()


class SignUp(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, password):
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
            return SignUp(user)
        except:
            raise GraphQLError('Something went wrong while creating user')


class Mutation(graphene.ObjectType):
    signup = SignUp.Field()


def update_user(data, user_id):
    user = User.objects.filter(id=user_id).update(**data)
    return user
