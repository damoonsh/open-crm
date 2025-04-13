using HotChocolate.Types;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.Models;
using TaskManagementApi.GraphQL.Resolvers;

namespace TaskManagementApi.GraphQL.Types
{
    public class TaskType : ObjectType<TaskItem>
    {
        protected override void Configure(IObjectTypeDescriptor<TaskItem> descriptor)
        {
            descriptor.Field(t => t.Id).Type<NonNullType<IdType>>();
            descriptor.Field(t => t.Title).Type<NonNullType<StringType>>();
            descriptor.Field(t => t.Description).Type<StringType>();
            descriptor.Field(t => t.Status).Type<EnumType<Status>>();
            descriptor.Field(t => t.DueDate).Type<DateTimeType>();
            descriptor.Field(t => t.CreatedAt).Type<NonNullType<DateTimeType>>();
            descriptor.Field(t => t.LastUpdated).Type<NonNullType<DateTimeType>>();
            descriptor.Field(t => t.CreatorId).Type<NonNullType<StringType>>();
            descriptor.Field(t => t.Priority).Type<EnumType<Priority>>();
            descriptor.Field(t => t.Category).Type<StringType>();
            descriptor.Field(t => t.Tags).Type<ListType<StringType>>();
            
            // Keep these relationship resolvers
            descriptor
                .Field("creator")
                .ResolveWith<TaskResolvers>(r => r.GetCreator(default!, default!))
                .Type<UserType>();
                
            descriptor
                .Field("comments")
                .ResolveWith<TaskResolvers>(r => r.GetComments(default!, default!))
                .Type<ListType<CommentType>>();
        }
    }
}