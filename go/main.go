package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"

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
func getBarcode(c *gin.Context) {
	barcode := c.DefaultQuery("barcode", "")
	if barcode == "" {
		c.AbortWithStatus(http.StatusNotFound)
		return
	}
	bc, err := barcodeFromCode(barcode)
	if err != nil {
		c.AbortWithError(http.StatusNotFound, err)
		return
	}
	c.JSON(http.StatusOK, bc)
}

func root(c *gin.Context) {
	c.String(200, "This is an API server, please use the correct client.")
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

	router := gin.New()
	router.Use(gin.Recovery())
	router.GET("/", root)
	router.GET("/barcode/lookup", getBarcode)

	router.Run("0.0.0.0:8080")
}
