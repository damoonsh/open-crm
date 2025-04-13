using HotChocolate;
using HotChocolate.Types;
using HotChocolate.Data;
using Microsoft.AspNetCore.Identity;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks; // Add this for async UserManager methods
using TaskManagementApi.Data;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL
{
    public class Query
    {
        [UsePaging]
        [UseFiltering]
        [UseSorting]
        // Rename parameter and inject UserManager
        public async Task<IQueryable<TaskItem>> GetTasksByCreator(
            string username,
            [Service] AppDbContext context,
            [Service] UserManager<IdentityUser> userManager)
        {
            // Find the user by username
            var user = await userManager.FindByNameAsync(username);
            Console.WriteLine($"User found: {user?.UserName}");
            if (user == null)
            {
                // Return an empty list if user not found
                return new List<TaskItem>().AsQueryable();
            }

            // Filter tasks by the found user's ID
            return context.Tasks.Where(t => t.CreatorId == user.UserName);
        }

        public TaskItem GetTaskById(int id, [Service] AppDbContext context)
        {
            return context.Tasks.FirstOrDefault(t => t.Id == id);
        }

        [UsePaging]
        [UseFiltering]
        [UseSorting]
        public IQueryable<IdentityUser> GetUsers([Service] AppDbContext context)
        {
            return context.Users;
        }

        public IdentityUser GetUser(string id, [Service] AppDbContext context)
        {
            return context.Users.FirstOrDefault(u => u.Id == id);
        }
    }
}