using HotChocolate.Types;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.Models;
using TaskManagementApi.GraphQL.Resolvers;

namespace TaskManagementApi.GraphQL.Types
{
    public class CommentType : ObjectType<Comment>
    {
        protected override void Configure(IObjectTypeDescriptor<Comment> descriptor)
        {
            descriptor.Field(c => c.Id).Type<NonNullType<IdType>>();
            descriptor.Field(c => c.Content).Type<NonNullType<StringType>>();
            descriptor.Field(c => c.CreatorId).Type<NonNullType<StringType>>();
            descriptor.Field(c => c.CreatedAt).Type<NonNullType<DateTimeType>>();
            descriptor.Field(c => c.LastUpdated).Type<DateTimeType>();
            
            // Define relationship resolvers
            descriptor
                .Field("task")
                .ResolveWith<CommentResolvers>(r => r.GetTask(default!, default!))
                .Type<TaskType>();
                
            descriptor
                .Field("CreatorId")
                .ResolveWith<CommentResolvers>(r => r.GetCreatorId(default!, default!))
                .Type<UserType>();
                
            descriptor
                .Field("replies")
                .ResolveWith<CommentResolvers>(r => r.GetReplies(default!, default!))
                .Type<ListType<CommentType>>();
        }
    }
}