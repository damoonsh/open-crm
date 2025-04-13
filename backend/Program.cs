using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using System.Text.Json;
using TaskManagementApi.Data;
using TaskManagementApi.GraphQL;
using TaskManagementApi.GraphQL.Types;
using TaskManagementApi.GraphQL.Mutations;
using TaskManagementApi.Models;
using Microsoft.AspNetCore.Authorization;
using HotChocolate.AspNetCore.Authorization;
using HotChocolate.Data;

var builder = WebApplication.CreateBuilder(args);

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

// Configure database
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// Add scoped AppDbContext
builder.Services.AddScoped<AppDbContext>();

// Configure Identity
builder.Services.AddIdentity<IdentityUser, IdentityRole>()
    .AddEntityFrameworkStores<AppDbContext>()
    .AddDefaultTokenProviders();

// Configure JWT Authentication
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    // Get the JWT secret from configuration, with a fallback
    var jwtSecret = builder.Configuration["JWT:Secret"] ?? 
        "FallbackSecretKeyFor1234567890DevelopmentOnly!@#$%^&*()";
        
    options.TokenValidationParameters = new TokenValidationParameters()
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidAudience = builder.Configuration["JWT:ValidAudience"] ?? "https://localhost:5263",
        ValidIssuer = builder.Configuration["JWT:ValidIssuer"] ?? "https://localhost:5263",
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
    };

    options.Events = new JwtBearerEvents
    {
        OnAuthenticationFailed = context =>
        {
            context.Response.StatusCode = 401;
            context.Response.ContentType = "application/json";
            var result = JsonSerializer.Serialize(new { message = "Authentication failed" });
            return context.Response.WriteAsync(result);
        },
        OnChallenge = context =>
        {
            context.HandleResponse();
            context.Response.StatusCode = 401;
            context.Response.ContentType = "application/json";
            var result = JsonSerializer.Serialize(new { message = "You are not authorized" });
            return context.Response.WriteAsync(result);
        }
    };
});

// Add Authorization
builder.Services.AddAuthorization();

// Add HttpContextAccessor (needed for authorization)
builder.Services.AddHttpContextAccessor();

// Configure GraphQL
builder.Services
    .AddGraphQLServer()
    .AddAuthorization()
    .AddQueryType<TaskManagementApi.GraphQL.Query>()
    .AddMutationType()
    .AddTypeExtension<AuthMutations>()
    .AddTypeExtension<TaskMutations>()
    .AddTypeExtension<CommentMutations>()
    .AddType<TaskType>()
    .AddType<CommentType>()
    .AddType<UserType>()
    .AddFiltering()
    .AddSorting()
    .AddProjections()
    .ModifyRequestOptions(opt => 
    {
        opt.IncludeExceptionDetails = builder.Environment.IsDevelopment();
    });

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    
    // Remove or comment out the Swagger middleware
    // app.UseSwagger();
    // app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseRouting();

// Add CORS middleware - must be between UseRouting and UseAuthorization
app.UseCors("AllowAll");

app.UseAuthentication();
app.UseAuthorization();

// Configure endpoints - ONLY GraphQL, no REST Controllers
app.MapGraphQL();

// Add health check endpoint
app.MapGet("/health", () => "Healthy");

app.Run();