import graphene
import users.schema
import graphql_jwt
import controllers.orgs
import controllers.applications


# As the app grows the Query and Mutation class will extend from more schemas
class Query(users.schema.Query,
            controllers.orgs.Query,
            controllers.applications,
            graphene.ObjectType):
    pass


class Mutation(users.schema.Mutation,
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)