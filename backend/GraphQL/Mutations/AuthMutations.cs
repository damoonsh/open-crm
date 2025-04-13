using HotChocolate;
using HotChocolate.Types;
using Microsoft.AspNetCore.Identity;
using System.Linq;
using System.Threading.Tasks;
using TaskManagementApi.GraphQL.Types.Inputs;
using TaskManagementApi.GraphQL.Types.Payloads;

namespace TaskManagementApi.GraphQL.Mutations
{
    [ExtendObjectType("Mutation")]
    public class AuthMutations : BaseMutation
    {
        public async Task<LoginPayload> Login(
            LoginInput input,
            [Service] UserManager<IdentityUser> userManager,
            [Service] SignInManager<IdentityUser> signInManager,
            [Service] IConfiguration config)
        {
            // Console.WriteLine(input.Username);
            var user = await userManager.FindByNameAsync(input.Username);
            if (user == null)
            {
                throw new GraphQLException("1Invalid username or password");
            }

            var result = await signInManager.CheckPasswordSignInAsync(user, input.Password, false);
            if (!result.Succeeded)
            {
                throw new GraphQLException("2Invalid username or password");
            }

            var jwtSecret = config["JWT:Secret"] ?? 
                "FallbackSecretKeyFor1234567890DevelopmentOnly!@#$%^&*()";
            var token = GenerateJwtToken(user, jwtSecret, config);
            
            return new LoginPayload
            {
                User = user,
                Token = token
            };
        }
        
        public async Task<RegisterPayload> Register(
            RegisterInput input,
            [Service] UserManager<IdentityUser> userManager,
            [Service] IConfiguration config)
        {
            // Check if the provided input is valid
            if (string.IsNullOrEmpty(input.Username) || string.IsNullOrEmpty(input.Password) || string.IsNullOrEmpty(input.Email))
            {
                throw new GraphQLException("Username, password, and email are required.");
            }

            var user = new IdentityUser
            {
                UserName = input.Username,
                Email = input.Email
            };

            var result = await userManager.CreateAsync(user, input.Password);
            if (!result.Succeeded)
            {
                var errors = string.Join(", ", result.Errors.Select(e => e.Description));
                throw new GraphQLException($"Failed to create user: {errors}");
            }

            var jwtSecret = config["JWT:Secret"] ?? 
                "FallbackSecretKeyFor1234567890DevelopmentOnly!@#$%^&*()";
            var token = GenerateJwtToken(user, jwtSecret, config);
            
            return new RegisterPayload
            {
                User = user,
                Token = token
            };
        }
    }
}