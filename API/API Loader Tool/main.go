package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

const (
	NbNsxAppliances       = 3
	NsxConcurrentSessions = 20
	TestSize              = 1000
	HApiBunches           = 2000
	UseHAPI               = false
	Verb                  = "PATCH" // Use PATCH or DELETE

	MaxRetries    = 5
	RetryMinDelay = 10
	RetryMaxDelay = 500

	NsxHost1    = "10.221.109.40"
	NsxHost2    = "10.221.109.41"
	NsxHost3    = "10.221.109.42"
	NsxUsername = "admin"
	NsxPassword = "VMware1!VMware1!"
	Prefix      = "MyPrefix"
)

var wg = sync.WaitGroup{}

type NsxAPIClient struct {
	Client   *http.Client
	Headers  map[string]string
	Host     string
	Username string
	Password string
}

type PatchGroup struct {
	Description string `json:"description"`
	DisplayName string `json:"display_name"`
}

type Infra struct {
	ResourceType string  `json:"resource_type,omitempty"`
	Description  string  `json:"description,omitempty"`
	DisplayName  string  `json:"display_name,omitempty"`
	ID           string  `json:"id,omitempty"`
	Children     []Infra `json:"children,omitempty"`
	Group        *Group  `json:"Group,omitempty"`
	TargetType   string  `json:"target_type,omitempty"`
}

type Group struct {
	ResourceType string `json:"resource_type,omitempty"`
	Description  string `json:"description,omitempty"`
	DisplayName  string `json:"display_name,omitempty"`
	ID           string `json:"id,omitempty"`
}

type APICall struct {
	Method string
	URI    string
	Body   interface{}
}

type Stat struct {
	NbRequests int
	NbRetries  int
	NbErrors   int
}

// Initialize Client for NSX communications
func NewNsxClient(host, username, password string, insecure bool) NsxAPIClient {

	client := new(http.Client)

	client.Transport = &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: insecure,
		},
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 100,
		MaxConnsPerHost:     100,
	}
	client.CheckRedirect = func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse
	}

	headers := map[string]string{
		"Accept":       "application/json",
		"Content-Type": "application/json",
	}

	return NsxAPIClient{
		Client:   client,
		Username: username,
		Password: password,
		Host:     host,
		Headers:  headers,
	}
}

func (c NsxAPIClient) CallAPI(verb, uri string, body interface{}) ([]byte, int, error) {

	uri = strings.TrimPrefix(uri, "/")
	uri = strings.TrimSuffix(uri, "/")
	baseURL := fmt.Sprintf("https://%s/%s", c.Host, uri)

	reqBody, err := json.Marshal(body)
	if err != nil {
		return nil, 500, err
	}

	//fmt.Println()
	//fmt.Println(string(reqBody))
	//fmt.Println()

	req, err := http.NewRequest(verb, baseURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, 500, err
	}
	req.SetBasicAuth(c.Username, c.Password)

	for k, h := range c.Headers {
		req.Header.Set(k, h)
	}

	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, 500, err
	}

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, 500, err
	}
	resp.Body.Close()

	if resp.StatusCode >= 400 {
		return respBody, resp.StatusCode, fmt.Errorf("error")
	}

	return respBody, resp.StatusCode, nil

}

func main() {

	client1 := NewNsxClient(NsxHost1, NsxUsername, NsxPassword, true)
	client2 := NewNsxClient(NsxHost2, NsxUsername, NsxPassword, true)
	client3 := NewNsxClient(NsxHost3, NsxUsername, NsxPassword, true)

	clientmap := []NsxAPIClient{}
	clientmap = append(clientmap, client1, client2, client3)

	stats := []Stat{}

	fmt.Println("☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢")
	fmt.Println("☢ Welcome to NSX API Loader ☢")
	fmt.Println("☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢☢")

	fmt.Println("Number of appliances: \t\t", NbNsxAppliances)
	fmt.Println("Number of API Calls: \t\t", TestSize)
	fmt.Println("Number of Concurrent Sessions: \t", NsxConcurrentSessions)
	fmt.Println("Use of HAPI: \t\t\t", UseHAPI)
	fmt.Println("Size of HAPI bunches: \t\t", HApiBunches)
	for n := 0; n < NbNsxAppliances; n++ {
		fmt.Printf("NSX%d: \t\t\t\t %s\n", n, clientmap[n].Host)
	}
	fmt.Println()

	fmt.Print("⚠ Are you sure to start? [Enter Y to confirm] ")
	var ch1 string
	if _, err := fmt.Scan(&ch1); err != nil {
		fmt.Println("Error:", err)
		os.Exit(1)
	}
	if ch1 != "Y" {
		fmt.Println("🚪 Exiting program ")
		os.Exit(0)
	}
	fmt.Println()

	// Load simulation
	fmt.Println("🖥 Generating APIs calls")
	apicalls := []APICall{}
	hapicalls := []APICall{}

	for j := 0; j < TestSize; j++ {
		apicalls = append(apicalls, APICall{
			Method: Verb,
			URI:    fmt.Sprintf("policy/api/v1/infra/domains/default/groups/group_%d", j),
			Body: PatchGroup{
				Description: fmt.Sprintf("group_%v_%d", Prefix, j),
				DisplayName: fmt.Sprintf("group_%v_%d", Prefix, j),
			},
		})
	}

	for j := 0; float64(j) <= math.Ceil(TestSize/HApiBunches); j++ {
		// Transform to HAPI
		body := Infra{
			ResourceType: "Infra",
			Children: []Infra{
				{
					ResourceType: "ChildResourceReference",
					ID:           "default",
					TargetType:   "Domain",
					Children:     []Infra{},
				},
			},
		}

		max := math.Min(float64(TestSize-(j*HApiBunches)), HApiBunches)

		for h := 0; float64(h) < max; h++ {
			body.Children[0].Children = append(body.Children[0].Children, Infra{
				ResourceType: "ChildGroup",
				Group: &Group{
					ResourceType: "Group",
					Description:  fmt.Sprintf("group_%v_%d", Prefix, (j*HApiBunches)+h),
					DisplayName:  fmt.Sprintf("group_%v_%d", Prefix, (j*HApiBunches)+h),
					ID:           fmt.Sprintf("group_%d", j+h),
				},
			})
		}

		if len(body.Children[0].Children) != 0 {
			hapicalls = append(hapicalls, APICall{
				Method: "PATCH",
				URI:    "policy/api/v1/infra",
				Body:   body,
			})
		}

	}

	//result, status, err := clientmap[0].CallAPI("PATCH", "policy/api/v1/infra", body)
	//fmt.Println(status, err, string(result))

	// Loading API calls
	fmt.Println("⚡ Loading API calls in memory")

	var ch chan APICall
	if UseHAPI {
		ch = make(chan APICall, len(hapicalls))
		for j := 0; j < len(hapicalls); j++ {
			ch <- hapicalls[j]
		}
	} else {
		ch = make(chan APICall, TestSize)
		for j := 0; j < TestSize; j++ {
			ch <- apicalls[j]
		}
	}
	close(ch)

	// Start timer
	ticker := time.NewTicker(100 * time.Millisecond)
	done := make(chan bool)
	nbRequestsDone := 0

	go func() {
		for {
			select {
			case <-done:
				return
			case <-ticker.C:
				fmt.Printf("\r⏳ Number of requests processed: %d. Number of requests to process: %d     ", nbRequestsDone, len(ch))
			}
		}
	}()

	// n go routines
	fmt.Println("🚀 Start processing API calls")
	now := time.Now()
	for n := 0; n < NbNsxAppliances; n++ {
		fmt.Println("Ⓝ Using NSX appliance ", clientmap[n].Host)
		wg.Add(1)
		stats = append(stats, Stat{})
		go func(n int) {

			for j := 0; j < NsxConcurrentSessions; j++ {
				wg.Add(1)
				//fmt.Println("test1")

				go func(n int) {
					for {
						if v, ok := <-ch; ok {
							for i := 0; i < MaxRetries; i++ {
								stats[n].NbRequests++
								if v.Method == "DELETE" {
									v.Body = nil
								}
								r, status, err := clientmap[n].CallAPI(v.Method, v.URI, v.Body)

								if err == nil {
									break
								}

								if status == 429 {
									stats[n].NbRetries++
									min := RetryMinDelay
									max := RetryMaxDelay
									if (max > 0) && (max-min != 0) {
										var interval int
										if max-min == 0 {
											interval = min
										} else {
											interval = i * (rand.Intn(max-min) + min)
										}

										time.Sleep(time.Duration(interval) * time.Millisecond)

									}
								} else {
									stats[n].NbErrors++
									fmt.Printf("❌ Error on %s. (%s. Status is %d. Result is %s) \n", clientmap[n].Host, err.Error(), status, string(r))
								}
							}
							nbRequestsDone++

						} else {
							wg.Done()
							break
						}
					}

				}(n)
			}

			wg.Done()

		}(n)
	}

	// Wait for all API calls to be processed
	wg.Wait()

	// Stop timer
	ticker.Stop()
	done <- true

	fmt.Println()
	fmt.Println("✅ End of API calls processing")

	fmt.Println()

	// Display some stats
	NbRequestsTotal := 0
	for n := 0; n < NbNsxAppliances; n++ {
		NbRequestsTotal += stats[n].NbRequests
	}

	for n := 0; n < NbNsxAppliances; n++ {
		fmt.Println("*******************************")
		fmt.Printf("Ⓝ NSX %s: \n", clientmap[n].Host)
		fmt.Printf("🔢 Number of API requests %d (%d%%): \n", stats[n].NbRequests, 100*stats[n].NbRequests/NbRequestsTotal)
		fmt.Printf("🔢 Number of API retries %d: (%d%%)\n", stats[n].NbRetries, 100*stats[n].NbRetries/NbRequestsTotal)
		fmt.Printf("🔢 Number of API errors %d: (%d%%)\n", stats[n].NbErrors, 100*stats[n].NbErrors/NbRequestsTotal)
	}
	// Display time
	fmt.Println()
	fmt.Println("🕓 Total time: ", time.Since(now))

	fmt.Println()

	//

}
