using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MusicEventManagementSystem.API.Migrations
{
    /// <inheritdoc />
    public partial class BrandSimilarBrands : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Existing brands were seeded from the recommender's own export, so it knows them all.
            migrationBuilder.AddColumn<bool>(
                name: "KnownToModel",
                table: "Brands",
                type: "boolean",
                nullable: false,
                defaultValue: true);

            migrationBuilder.AddColumn<string>(
                name: "SimilarBrands",
                table: "Brands",
                type: "character varying(300)",
                maxLength: 300,
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "KnownToModel",
                table: "Brands");

            migrationBuilder.DropColumn(
                name: "SimilarBrands",
                table: "Brands");
        }
    }
}
