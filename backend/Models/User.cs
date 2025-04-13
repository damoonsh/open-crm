using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace TaskManagementApi.Models
{
    public class User
    {
        [Key]
        public required string Id { get; set; } = Guid.NewGuid().ToString();
        
        [Required]
        [StringLength(50, MinimumLength = 3)]
        public required string UserName { get; set; } = null!;
        
        [EmailAddress]
        public required string Email { get; set; } = null!;
        
        [Required]
        public required string Password { get; set; } = null!;
    }
}