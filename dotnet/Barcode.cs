namespace dotnetspeedtest;

public record Barcode
{
    public long Id { get; set; }

    public string Code { get; set; }

    public BarcodeStatus Status { get; set; }
}
