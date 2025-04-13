using HotChocolate;
using HotChocolate.Types;
using Microsoft.AspNetCore.Identity;
using System.Collections.Generic;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Resolvers
{
    public class UserResolvers
    {
        public IEnumerable<TaskItem> GetCreatedTasks([Parent] IdentityUser user, [Service] AppDbContext dbContext)
        {
            return dbContext.Tasks.Where(t => t.CreatorId == user.Id).ToList();
        }
    }
}