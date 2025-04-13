using System.ComponentModel.DataAnnotations;

namespace TaskManagementApi.Models;

public class TaskItem
{
    public required int Id { get; set; } 
    public required string Title { get; set; }
    public required string Description { get; set; }
    public Status Status { get; set; } = Status.Pending;
    public DateTime? DueDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? LastUpdated { get; set; } = DateTime.UtcNow;
    [Required]
    public string CreatorId { get; set; } = null!;
    // public ICollection<TaskAssignment>? TaskAssignments { get; set; }
    public Priority? Priority { get; set; }
    public string? Category { get; set; }
    public List<string>? Tags { get; set; }
}

public enum Status
{
    Pending,
    In_Progress,
    Completed,
    On_Hold,
    Cancelled
}

public enum Priority
{
    Low,
    Medium,
    High,
    Urgent
}