using Microsoft.AspNetCore.SignalR;

namespace TaskManagementApi.Hubs;

public class TaskHub : Hub
{
    public async Task SendTaskUpdate(string taskId)
    {
        await Clients.All.SendAsync("TaskUpdated", taskId);
    }
}