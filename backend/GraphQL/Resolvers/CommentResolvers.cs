using HotChocolate;
using HotChocolate.Types;
using HotChocolate.Resolvers;
using System.Linq;
using Microsoft.AspNetCore.Identity;
using TaskManagementApi.Data;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Resolvers
{
    public class CommentResolvers
    {
        public IQueryable<Comment> GetReplies([Parent] Comment comment, [Service] AppDbContext dbContext)
        {
            return dbContext.Comments.Where(c => c.ParentCommentId == comment.Id);
        }
        
        public TaskItem GetTask([Parent] Comment comment, [Service] AppDbContext dbContext)
        {
            return dbContext.Tasks.FirstOrDefault(t => t.Id == comment.TaskId);
        }

        public IQueryable<Comment> GetComments([Parent] TaskItem task, [Service] AppDbContext dbContext)
        {
            return dbContext.Comments.Where(c => c.TaskId == task.Id && c.ParentCommentId == null);
        }
        
        public IdentityUser GetCreatorId([Parent] Comment comment, [Service] AppDbContext dbContext)
        {
            return dbContext.Users.FirstOrDefault(u => u.Id == comment.CreatorId);
        }
    }
}