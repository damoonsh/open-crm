using HotChocolate.Types;
using HotChocolate.Authorization;
using System.Collections.Generic;

namespace TaskManagementApi.GraphQL
{
    public static class AuthExtensions
    {
        public static IObjectFieldDescriptor RequireAuthorization(this IObjectFieldDescriptor descriptor)
        {
            return descriptor.Authorize();
        }
        
        public static IObjectFieldDescriptor RequireAuthorization(this IObjectFieldDescriptor descriptor, string policy)
        {
            return descriptor.Authorize(policy);
        }
        
        public static IObjectFieldDescriptor RequireAuthorization(this IObjectFieldDescriptor descriptor, params string[] roles)
        {
            return descriptor.Authorize(roles);
        }
    }
}