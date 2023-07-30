package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/recover"

	_ "github.com/go-sql-driver/mysql"
)

type barcodeType string

// album represents data about a record album.
type barcode struct {
	Id     int64       `json:"id"`
	Code   string      `json:"code"`
	Status barcodeType `json:"status"`
}

const (
	created    barcodeType = "created"
	downloaded barcodeType = "downloaded"
	used       barcodeType = "used"
	returned   barcodeType = "returned"
	expired    barcodeType = "expired"
)

func barcodeFromCode(code string) (barcode, error) {
	// A barcode to hold data from the returned row.
	var bc barcode

	row := db.QueryRow("select barcode_id as Id, barcode as Code, status as Status from barcodes where barcode = ?", code)
	if err := row.Scan(&bc.Id, &bc.Code, &bc.Status); err != nil {
		if err == sql.ErrNoRows {
			return bc, fmt.Errorf("barcodeFromCode %s: no such barcode", code)
		}
		return bc, fmt.Errorf("barcodeFromCode %s: %v", code, err)
	}
	return bc, nil
}

// getBarcode responds with the scanned barcode.
func getBarcode(c *fiber.Ctx) error {
	barcode := c.Query("barcode", "")
	if barcode == "" {
		return fiber.ErrNotFound
	}
	bc, err := barcodeFromCode(barcode)
	if err != nil {
		return fiber.ErrNotFound
	}
	c.Status(http.StatusOK).JSON(bc)
	return nil
}

func root(c *fiber.Ctx) error {
	c.Status(http.StatusOK).SendString("This is an API server, please use the correct client.")

	return nil
}

var db *sql.DB

func main() {
	connectionString := os.Getenv("MYSQL_CONNECTION_STRING")
	if connectionString == "" {
		connectionString = "root:testpassword@(percona:33306)/speedtest"
	}
	var err error
	db, err = sql.Open("mysql", connectionString)
	if err != nil {
		panic(err)
	}
	defer db.Close()
	// See "Important settings" section.
	db.SetConnMaxLifetime(time.Minute * 3)
	db.SetMaxOpenConns(100)
	db.SetMaxIdleConns(2)

	app := fiber.New()
	app.Use(recover.New())
	app.Get("/", root)
	app.Get("/barcode/lookup", getBarcode)

	app.Listen(":8080")
}
