using Dapper;

using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

using MySql.Data.MySqlClient;

namespace dotnetspeedtest.Pages
{
    public class BarcodeModel : PageModel
    {
        public Barcode Barcode { get; set; }

        public bool HasBarcode => Barcode != null;

        [FromQuery(Name = "barcode")]
        public string RawBarcode { get; set; }

        private readonly MySqlConnection connection;


        public BarcodeModel(MySqlConnection conn)
        {
            connection = conn;
        }

        public void OnGet()
        {
            var b = connection.QueryFirstOrDefault<Barcode>("select barcode_id as Id, barcode as Code, status as Status from barcodes where barcode = @barcode", new { barcode = RawBarcode });

            if (b is Barcode bc)
            {
                Barcode = bc;
            }
            else
            {
                Response.StatusCode = 404;
            }
        }
    }
}
