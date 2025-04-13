using HotChocolate.Types;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.GraphQL.Resolvers;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Types
{
    public class UserType : ObjectType<User>
    {
        protected override void Configure(IObjectTypeDescriptor<User> descriptor)
        {
            descriptor.Field(u => u.Id).Type<NonNullType<IdType>>();
            descriptor.Field(u => u.UserName).Type<NonNullType<StringType>>();
            descriptor.Field(u => u.Email).Type<StringType>();
            
            // Exclude sensitive fields
            descriptor.Ignore(u => u.Password);
            
            // Keep this resolver
            descriptor
                .Field("createdTasks")
                .ResolveWith<UserResolvers>(r => r.GetCreatedTasks(default!, default!))
                .Type<ListType<TaskType>>();
        }
    }
}