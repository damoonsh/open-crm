using HotChocolate;
using HotChocolate.Types;
using Microsoft.AspNetCore.Identity;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Resolvers
{
    public class TaskResolvers
    {
        public IdentityUser GetCreator([Parent] TaskItem task, [Service] AppDbContext dbContext)
        {
            return dbContext.Users.FirstOrDefault(u => u.Id == task.CreatorId);
        }

        public IQueryable<Comment> GetComments([Parent] TaskItem task, [Service] AppDbContext dbContext)
        {
            return dbContext.Comments.Where(c => c.TaskId == task.Id && c.ParentCommentId == null);
        }
    }
}