using Microsoft.AspNetCore.Identity;

namespace TaskManagementApi.GraphQL.Types.Payloads
{
    public class LoginPayload
    {
        public required IdentityUser User { get; set; }
        public required string Token { get; set; }
    }
    
    public class RegisterPayload
    {
        public required IdentityUser User { get; set; }
        public required string Token { get; set; }
    }
}