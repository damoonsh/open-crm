using System;
using System.Collections.Generic;
using TaskManagementApi.Models;

namespace TaskManagementApi.GraphQL.Types.Inputs
{
    public class CreateTaskInput
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public Status Status { get; set; } = Status.Pending;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime? DueDate { get; set; } = DateTime.UtcNow;
        public string CreatorId { get; set; } = null!;
        public Priority? Priority { get; set; }
        public string? Category { get; set; }
        public List<string>? Tags { get; set; }
        public DateTime? LastUpdated { get; set; } = DateTime.UtcNow;
    }
    
    public class UpdateTaskInput
    {
        public int? Id { get; set; }
        public string? Title { get; set; }
        public string? Description { get; set; }
        public Status? Status { get; set; }
        public DateTime? DueDate { get; set; }
        public Priority? Priority { get; set; }
        public string? Category { get; set; }
        public List<string>? Tags { get; set; }
    }
    
    public class AssignTaskInput
    {
        public int TaskId { get; set; }
        public string UserId { get; set; }
    }
    
    public class UnassignTaskInput
    {
        public int TaskId { get; set; }
        public string UserId { get; set; }
    }
}