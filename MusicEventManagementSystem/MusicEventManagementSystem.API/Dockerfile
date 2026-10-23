# ASP.NET Core 8 API. Build context: this folder.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY MusicEventManagementSystem.API.csproj ./
RUN dotnet restore
COPY . ./
RUN dotnet publish -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app ./
ENV ASPNETCORE_URLS=http://+:5255
EXPOSE 5255
ENTRYPOINT ["dotnet", "MusicEventManagementSystem.API.dll"]
