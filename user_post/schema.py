import graphene
from graphene_django import DjangoObjectType
from .models import User, Post


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "name", "email")


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "date_posted", "last_updated", "author")


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_posts = graphene.List(PostType)

    def resolve_all_users(root, info):
        return User.objects.all()

    def resolve_all_posts(root, info):
        return Post.objects.all()


class UserAddMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, email, password):
        user = User(name=name, email=email, password=password)
        user.save()
        return UserAddMutation(user=user, ok="Successfully added user!")


class UserEditMutation(graphene.Mutation):

    class Arguments:
        _id = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, _id, password):
        user = User.objects.get(id=_id)
        user.password = password
        user.save()
        return UserEditMutation(user=user, ok="Successfully changed password")


class UserDeleteMutation(graphene.Mutation):

    class Arguments:
        _id = graphene.String(required=True)

    user = graphene.Field(UserType)
    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, _id):
        user = User.objects.get(id=_id)
        user.delete()
        return UserDeleteMutation(user=user, ok="Successfully deleted user!")


class PostAddMutation(graphene.Mutation):

    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        author_id = graphene.String(required=True)

    post = graphene.Field(PostType)
    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, title, content, author_id):
        author = User.objects.get(id=author_id)
        if author is None:
            return f"No author with id = {author_id} found!"
        post = Post(title=title,content=content,author=author)
        post.save()
        return PostAddMutation(post=post, ok="Successfully added post!")


class PostEditMutation(graphene.Mutation):

    class Arguments:
        post_id = graphene.String(required=True)
        title = graphene.String(required=False)
        content = graphene.String(required=True)

    post = graphene.Field(PostType)
    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, post_id, content, title=None):
        post = Post.objects.get(id=post_id)
        if title is not None:
            post.title = title
        post.content = content
        post.save()
        return PostEditMutation(post=post, ok="Successfully edited post!")


class PostDeleteMutation(graphene.Mutation):

    class Arguments:
        post_id = graphene.String(required=True)

    ok = graphene.String()

    @classmethod
    def mutate(cls, root, info, post_id):
        post = Post.objects.get(id=post_id)
        post.delete()
        return PostDeleteMutation(ok="Successfully deleted post!")


class Mutation(graphene.ObjectType):
    # Api calls related to user management
    add_user = UserAddMutation.Field()
    edit_user = UserEditMutation.Field()
    delete_user = UserDeleteMutation.Field()

    # Api calls related to user post management
    add_post = PostAddMutation.Field()
    edit_post = PostEditMutation.Field()
    delete_post = PostDeleteMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
