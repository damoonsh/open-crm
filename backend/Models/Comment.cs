using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace TaskManagementApi.Models
{
    public class Comment
    {
        [Key]
        public required int Id { get; set; }

        // We only need the TaskId foreign key
        public required int TaskId { get; set; }

        public required string Content { get; set; }

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime? LastUpdated { get; set; }

        public required string CreatorId { get; set; }

        // For reply functionality
        public int? ParentCommentId { get; set; }
        
        // We can keep the Replies collection for convenience
        [ForeignKey("ParentCommentId")]
        public virtual ICollection<Comment>? Replies { get; set; } = new List<Comment>();
    }
}