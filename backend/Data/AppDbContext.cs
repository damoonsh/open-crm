using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using TaskManagementApi.Models;
using Microsoft.AspNetCore.Identity;

namespace TaskManagementApi.Data
{
    public class AppDbContext : IdentityDbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }

        public DbSet<TaskItem> Tasks { get; set; } = null!;
        public DbSet<Comment> Comments { get; set; } = null!;

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Add new Comment relationships
            modelBuilder.Entity<Comment>(entity =>
            {
                // Configure the TaskItem-Comment relationship
                entity.HasOne<TaskItem>()  
                    .WithMany()      
                    .HasForeignKey(c => c.TaskId)
                    .HasConstraintName("FK_Comments_Tasks")
                    .OnDelete(DeleteBehavior.Cascade);
                
                // Configure self-referencing relationship for comments
                entity.HasMany(c => c.Replies)
                    .WithOne()  
                    .HasForeignKey(c => c.ParentCommentId)
                    .HasConstraintName("FK_Comments_ParentComments")
                    .OnDelete(DeleteBehavior.Restrict);
            });
        }
    }
}