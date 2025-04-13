using HotChocolate;
using HotChocolate.Types;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using System;
using System.Linq;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using TaskManagementApi.Data;
using TaskManagementApi.GraphQL.Types.Inputs;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Mutations
{
    [ExtendObjectType("Mutation")]
    public class TaskMutations
    {
        public async Task<TaskItem> CreateTask(
            CreateTaskInput input,
            [Service] AppDbContext context)
        {
            var task = new TaskItem
            {
                Id = input.Id,
                Title = input.Title,
                Description = input.Description,
                Status = input.Status,
                DueDate = input.DueDate,
                CreatorId = input.CreatorId, // Assuming input.CreatorId is the username
                Priority = input.Priority,
                Category = string.IsNullOrWhiteSpace(input.Category) ? "" : input.Category,
                Tags = input.Tags?.Count > 0 ? input.Tags : new List<string>(),
                CreatedAt = DateTime.UtcNow,
                LastUpdated = DateTime.UtcNow // Set LastUpdated on creation too
            };

            context.Tasks.Add(task);
            await context.SaveChangesAsync();
            return task;
        }

        [Authorize]
        public async Task<TaskItem> UpdateTask(
            UpdateTaskInput input,
            [Service] AppDbContext context,
            [Service] IHttpContextAccessor httpContextAccessor,
            CancellationToken cancellationToken)
        {
            // Get the current user's USERNAME from the JWT token
            // Assuming the 'Name' claim holds the username
            var currentUsername = httpContextAccessor.HttpContext!.User.FindFirst(ClaimTypes.Name)?.Value;
            if (string.IsNullOrEmpty(currentUsername))
            {
                // Fallback or alternative claim check if needed
                currentUsername = httpContextAccessor.HttpContext!.User.Identity?.Name;
                if (string.IsNullOrEmpty(currentUsername))
                {
                    throw new UnauthorizedAccessException("User is not authenticated or username claim is missing");
                }
            }

            var task = await context.Tasks.FindAsync(new object[] { input.Id }, cancellationToken);
            if (task == null)
            {
                throw new GraphQLException($"Task with ID {input.Id} not found");
            }

            // Check if the current user's USERNAME matches the task's CreatorId (assuming CreatorId stores username)
            if (task.CreatorId != currentUsername)
            {
                throw new UnauthorizedAccessException($"User '{currentUsername}' cannot update task created by '{task.CreatorId}'");
            }

            // Proceed with update if authorized
            if (input.Title != null) task.Title = input.Title;
            if (input.Description != null) task.Description = input.Description;
            if (input.Status.HasValue) task.Status = input.Status.Value;
            if (input.DueDate.HasValue) task.DueDate = input.DueDate;
            if (input.Priority.HasValue) task.Priority = input.Priority;
            if (input.Category != null) task.Category = input.Category;
            if (input.Tags != null) task.Tags = input.Tags;

            task.LastUpdated = DateTime.UtcNow;

            await context.SaveChangesAsync(cancellationToken);
            return task;
        }

        [Authorize]
        public async Task<bool> DeleteTask(
            int id,
            string requestor_username,
            [Service] AppDbContext dbContext,
            [Service] IHttpContextAccessor httpContextAccessor,
            CancellationToken cancellationToken)
        {
            // Find the task by ID
            var task = await dbContext.Tasks.FindAsync(new object[] { id }, cancellationToken);
            if (task == null)
            {
                // Return false instead of throwing ArgumentException for a cleaner GraphQL response
                return false;
            }

            // Check if the current user's USERNAME matches the task's CreatorId (assuming CreatorId stores username)
            if (task.CreatorId != requestor_username)
            {
                throw new UnauthorizedAccessException($"User '{requestor_username}' cannot delete task created by '{task.CreatorId}'");
            }

            // Proceed with deletion if authorized
            dbContext.Tasks.Remove(task);
            await dbContext.SaveChangesAsync(cancellationToken);
            Console.WriteLine($"Task {id} deleted successfully by user '{requestor_username}'."); // Added log
            return true;
        }
    }
}