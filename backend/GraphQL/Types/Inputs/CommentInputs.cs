namespace TaskManagementApi.GraphQL.Types.Inputs
{
    public class AddCommentInput
    {
        public int Id { get; set; }
        public int TaskId { get; set; }
        public string Content { get; set; }
        public string CreatorId { get; set; }
        public int? ParentCommentId { get; set; }
    }
    
    public class UpdateCommentInput
    {
        public int Id { get; set; }
        public string Content { get; set; }
    }
}