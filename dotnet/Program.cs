using System.Net.Mime;
using System.Text;
using System.Text.Json.Serialization;

using Dapper;

using dotnetspeedtest;

using Microsoft.AspNetCore.Http.Json;
using MySql.Data.MySqlClient;



var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorPages();
builder.Services.Configure<JsonOptions>(o => o.SerializerOptions.Converters.Add(new JsonStringEnumConverter()));
//builder.Services.Configure<MvcJsonOptions>(o => o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

builder.Services.AddTransient<MySqlConnection>(_ =>
    new MySqlConnection(builder.Configuration.GetConnectionString("MySQL")));

//// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
//builder.Services.AddEndpointsApiExplorer();
//builder.Services.AddSwaggerGen();

var app = builder.Build();

//// Configure the HTTP request pipeline.
//if (app.Environment.IsDevelopment())
//{
//    app.UseSwagger();
//    app.UseSwaggerUI();
//}

app.MapRazorPages();

app.MapGet("/", () => Results.Ok("This is an API server, please use the correct client."));

app.MapGet("/barcode/lookupAsync", async (string barcode, MySqlConnection conn) =>{
    var b = await conn.QueryFirstOrDefaultAsync<Barcode>("select barcode_id as Id, barcode as Code, status as Status from barcodes where barcode = @barcode", new { barcode });
    
    return b switch
    {
        Barcode bc => Results.Ok(bc),
        _ => Results.NotFound()
    };
});

app.MapGet("/barcode/lookup", (string barcode, MySqlConnection conn) => {    
    var b = conn.QueryFirstOrDefault<Barcode>("select barcode_id as Id, barcode as Code, status as Status from barcodes where barcode = @barcode", new { barcode });
    
    return b switch
    {
        Barcode bc => Results.Ok(bc),
        _ => Results.NotFound()
    };
});


app.Run();
