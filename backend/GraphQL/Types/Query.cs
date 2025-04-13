using HotChocolate;
using HotChocolate.Data;
using HotChocolate.Types;
using System.Linq;
using TaskManagementApi.Data;
using TaskManagementApi.Models;

public class Query
{
    [UsePaging]
    [UseProjection]
    [UseFiltering]
    [UseSorting]
    public IQueryable<TaskItem> UserTasks(
        [Service] AppDbContext dbContext,
        string userId)
    {
        return dbContext.Tasks
            .Where(t => t.CreatorId == userId);
    }
}
