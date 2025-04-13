using HotChocolate;
using HotChocolate.Types;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TaskManagementApi.Data;
using TaskManagementApi.GraphQL.Types.Inputs;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Mutations
{
    [ExtendObjectType("Mutation")]
    public class CommentMutations
    {
        public async Task<Comment> AddComment(
            AddCommentInput input,
            [Service] AppDbContext context)
        {
            var comment = new Comment
            {
                Id = input.Id,
                Content = input.Content,
                TaskId = input.TaskId,
                CreatorId = input.CreatorId,
                ParentCommentId = input.ParentCommentId,
                CreatedAt = DateTime.UtcNow
            };
            
            context.Comments.Add(comment);
            await context.SaveChangesAsync();
            
            return comment;
        }
        
        public async Task<Comment> UpdateComment(
            UpdateCommentInput input,
            [Service] AppDbContext context)
        {
            var comment = await context.Comments.FindAsync(input.Id);
            if (comment == null)
            {
                throw new GraphQLException($"Comment with ID {input.Id} not found");
            }
            
            comment.Content = input.Content;
            comment.LastUpdated = DateTime.UtcNow;
            
            await context.SaveChangesAsync();
            return comment;
        }
        
        public async Task<Comment> DeleteComment(
            int id,
            [Service] AppDbContext context)
        {
            var comment = await context.Comments.FindAsync(id);
            if (comment == null)
            {
                throw new GraphQLException($"Comment with ID {id} not found");
            }
            
            // Get all comments for this task to find replies
            var allTaskComments = await context.Comments
                .Where(c => c.TaskId == comment.TaskId)
                .ToListAsync();
            
            // Build the reply tree for this comment
            if (comment.ParentCommentId == null)
            {
                OrganizeReplies(comment, allTaskComments);
            }
            
            // Delete all replies recursively
            DeleteRepliesRecursively(comment, context);
            
            // Delete the comment itself
            context.Comments.Remove(comment);
            await context.SaveChangesAsync();
            
            return comment;
        }
        
        // Helper methods
        private void OrganizeReplies(Comment comment, List<Comment> allComments)
        {
            comment.Replies = allComments
                .Where(c => c.ParentCommentId == comment.Id)
                .OrderBy(c => c.CreatedAt)
                .ToList();
            
            foreach (var reply in comment.Replies)
            {
                OrganizeReplies(reply, allComments);
            }
        }
        
        private void DeleteRepliesRecursively(Comment comment, AppDbContext context)
        {
            if (comment.Replies != null && comment.Replies.Any())
            {
                foreach (var reply in comment.Replies.ToList())
                {
                    DeleteRepliesRecursively(reply, context);
                    context.Comments.Remove(reply);
                }
            }
        }
    }
}