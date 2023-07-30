# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/dotnet/nightly/sdk:8.0-preview as build-env
WORKDIR /src
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /publish

FROM mcr.microsoft.com/dotnet/nightly/aspnet:8.0-preview as runtime
WORKDIR /publish
COPY --from=build-env /publish .
EXPOSE 80
ENTRYPOINT ["dotnet", "dotnet-speedtest.dll"]
