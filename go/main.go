package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"

	_ "github.com/go-sql-driver/mysql"

	"github.com/CloudyKit/jet/v6"
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

var views = jet.NewSet(
	jet.NewOSFileSystemLoader("./views"),
	//jet.InDevelopmentMode(), // remove in production
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

func makeNotFoundTemplate(c *gin.Context, orig_err error) {
	vars := make(jet.VarMap)
	t, err := views.GetTemplate("not-found.jet")
	if err != nil {
		// template could not be loaded, log the error?
		c.AbortWithError(http.StatusInternalServerError, err)
	}
	vars.Set("err", orig_err)
	if err = t.Execute(c.Writer, vars, nil); err != nil {
		// log the error
		c.AbortWithError(http.StatusInternalServerError, err)
	}
}

// getBarcode responds with the scanned barcode.
func getBarcodeTemplate(c *gin.Context) {

	barcode := c.DefaultQuery("barcode", "")
	if barcode == "" {
		makeNotFoundTemplate(c, nil)
		return
	}
	bc, err := barcodeFromCode(barcode)
	if err != nil {
		makeNotFoundTemplate(c, err)
		return
	}
	vars := make(jet.VarMap)
	vars.Set("barcode", bc)
	t, err := views.GetTemplate("barcode.jet")
	if err != nil {
		// template could not be loaded, log the error?
		makeNotFoundTemplate(c, err)
	}
	//c.Writer.WriteHeader(http.StatusOK)
	if err = t.Execute(c.Writer, vars, nil); err != nil {
		// log the error
		makeNotFoundTemplate(c, err)
	}
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
	router.GET("/barcode/template", getBarcodeTemplate)

	router.Run("0.0.0.0:8080")
}
