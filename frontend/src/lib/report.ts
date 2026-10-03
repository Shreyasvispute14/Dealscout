const reportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>DealScout Project Report</title>
<style>
  @page { size: A4; margin: 1in; }
  body { font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.5; color: #000; }
  h1 { font-size: 20pt; text-align: center; margin: 0 0 18pt; }
  h2 { font-size: 16pt; margin: 22pt 0 10pt; }
  h3 { font-size: 14pt; margin: 16pt 0 8pt; }
  p, li { font-size: 12pt; }
  .center { text-align: center; }
  .title-page { min-height: 9.5in; text-align: center; page-break-after: always; }
  .certificate { min-height: 9.5in; page-break-after: always; }
  .page-break { page-break-before: always; }
  .spacer { height: 28pt; }
  .large-spacer { height: 70pt; }
  .field { display: inline-block; min-width: 220pt; border-bottom: 1px solid #000; }
  table { width: 100%; border-collapse: collapse; margin: 10pt 0 18pt; }
  th, td { border: 1px solid #000; padding: 6pt; vertical-align: top; }
  th { font-weight: bold; }
  .diagram { border: 1px solid #000; min-height: 90pt; padding: 18pt; text-align: center; margin: 10pt 0; }
  .footer-note { margin-top: 50pt; text-align: center; font-size: 10pt; }
</style>
</head>
<body>
  <section class="title-page">
    <p class="center"><strong>KANNADA SANGHA PUNE'S</strong></p>
    <p class="center"><strong>KAVERI COLLEGE OF ARTS, SCIENCE &amp; COMMERCE</strong></p>
    <p class="center">Sr. No. 36, Shri G.M. Shetty Educational Complex, Ganeshnagar, Erandwane, Pune 411038.</p>
    <div class="large-spacer"></div>
    <h1>A PROJECT REPORT ON</h1>
    <h1>DEALSCOUT</h1>
    <p class="center">An E-Commerce Product Comparison and Best-Deal Recommendation System</p>
    <div class="spacer"></div>
    <p class="center">In partial fulfilment of B. Sc. (Computer Science)</p>
    <p class="center"><strong>TYBSC(CS) (SEM – V)</strong></p>
    <div class="large-spacer"></div>
    <p class="center">Submitted by</p>
    <p class="center">Name 1: <span class="field"></span> &nbsp; Seat No.: <span class="field"></span></p>
    <p class="center">Name 2: <span class="field"></span> &nbsp; Seat No.: <span class="field"></span></p>
    <p class="center"><strong>Academic Year 2026–27</strong></p>
  </section>

  <section class="certificate">
    <p class="center"><strong>KANNADA SANGHA PUNE'S KAVERI COLLEGE OF ARTS, SCIENCE &amp; COMMERCE</strong></p>
    <p class="center">PERMANENTLY AFFILIATED TO SAVITRIBAI PHULE PUNE UNIVERSITY, PUNE</p>
    <div class="spacer"></div>
    <h1>CERTIFICATE</h1>
    <p>This is to certify that Mr. / Ms. <span class="field"></span>, T.Y. BSc (Computer Science) Semester V, has successfully completed his/her Project Work titled <strong>DealScout</strong> in Computer Science Specialization as a part of CS-331-FP Project as prescribed by Savitribai Phule Pune University for academic year 2026–27.</p>
    <p>Seat No.: <span class="field"></span></p>
    <div class="large-spacer"></div>
    <table><tr><td>Project Guide<br /><br />Name: ____________________<br />Signature: ________________</td><td>Course Coordinator<br /><br />Name: ____________________<br />Signature: ________________</td><td>Principal<br /><br />Name: ____________________<br />Signature: ________________</td></tr></table>
    <h2 class="center">Examined by</h2>
    <table><tr><td>Internal Examiner<br /><br />Name: ____________________<br />Signature: ________________<br />Date: ____________________</td><td>External Examiner<br /><br />Name: ____________________<br />Signature: ________________<br />Date: ____________________</td></tr></table>
  </section>

  <section class="page-break">
    <h1>INDEX</h1>
    <table>
      <tr><th>Sr. No.</th><th>Chapter / Section</th><th>Page No.</th></tr>
      <tr><td>1</td><td>Preliminary Investigation<br />1.1 Problem Identification<br />1.2 Problem Statement / Definition<br />1.3 Purpose / Objective and Goals<br />1.4 Feasibility Study<br />1.5 Project Scope and Limitations</td><td></td></tr>
      <tr><td>2</td><td>Requirement Specification<br />2.1 System Requirements<br />2.2 Technical Requirement<br />2.3 Functional Requirements<br />2.4 Data Requirements</td><td></td></tr>
      <tr><td>3</td><td>Database Design<br />3.1 End Users<br />3.2 Entities and Attributes through ER Diagram<br />3.3 Tables, Fields, and Relationships</td><td></td></tr>
      <tr><td>4</td><td>System Design<br />4.1 Class Diagram<br />4.2 Object Diagram<br />4.3 Component Diagram<br />4.4 Deployment Diagram<br />4.5 Use Case Diagram<br />4.6 Activity Diagram<br />4.7 Sequence Diagram</td><td></td></tr>
      <tr><td>5</td><td>Input and Output Screen Layout<br />5.1 Login, Registration, and Add Record Screens<br />5.2 Dashboard, Search Result, and Report Screens</td><td></td></tr>
      <tr><td>6</td><td>Bibliography / References</td><td></td></tr>
    </table>
  </section>

  <section class="page-break">
    <h1>CHAPTER 1: PRELIMINARY INVESTIGATION</h1>
    <h2>1.1 Problem Identification</h2><p>Online shoppers often compare the same product across several e-commerce websites manually. Prices, discounts, ratings, delivery estimates, and sellers are presented in different formats, making it difficult to choose a suitable deal quickly.</p>
    <h2>1.2 Problem Statement / Definition</h2><p>Design and develop DealScout, a web-based product comparison system that accepts a product search, collects product offers from a demo catalog and optional live shopping provider, normalizes the fields, and recommends the lowest listed deal.</p>
    <h2>1.3 Purpose / Objective and Goals</h2><ul><li>Provide one search interface for multiple product sources.</li><li>Compare seller, price, discount, rating, and delivery fields.</li><li>Highlight the best possible listed price using a simple comparison algorithm.</li><li>Record collected searches for project analysis and demonstration.</li><li>Provide a login page and an academic project report structure.</li></ul>
    <h2>1.4 Feasibility Study</h2><h3>Technical Feasibility</h3><p>The system uses HTML/CSS/JavaScript-level UI concepts, a Python REST backend, JSON data exchange, and a document data store. The demo catalog works without external keys.</p><h3>Economic Feasibility</h3><p>The project uses freely available development tools. The optional live provider can be enabled later according to its plan and terms.</p><h3>Operational Feasibility</h3><p>A student can search, compare, and review collected data without technical knowledge of the backend.</p><h3>Schedule Feasibility</h3><p>The MVP is divided into login, search, comparison, analytics, and documentation modules, which can be developed and tested as separate tasks.</p>
    <h2>1.5 Project Scope and Limitations</h2><p>Scope includes mobiles, laptops, and general products with normalized offer fields. Live results depend on a configured provider key. Without a key, the interface uses a clearly labelled MOCKED LIVE PREVIEW and must not be treated as current retailer data.</p>

    <h1 class="page-break">CHAPTER 2: REQUIREMENT SPECIFICATION</h1>
    <h2>2.1 System Requirements</h2><p><strong>Hardware:</strong> Computer with 4 GB RAM or more, 2 GB available storage, keyboard, mouse, and internet connection for optional live results.</p><p><strong>Software:</strong> Modern browser, Python 3.11 or later, FastAPI/uvicorn development server, MongoDB for the running demo, and a code editor.</p>
    <h2>2.2 Technical Requirement</h2><p>Frontend: React with TypeScript, HTML5, CSS3, and browser form concepts. Backend: Python FastAPI, REST endpoints, JSON, and MongoDB collections representing the SQLite-style entities. Optional live adapter: SerpApi shopping provider configured on the server.</p>
    <h2>2.3 Functional Requirements</h2><ol><li>User can open the login page with demo credentials.</li><li>User can search products and select All, Mobiles, Laptops, or General category.</li><li>User can switch between Demo catalog and Live mode.</li><li>System displays seller, price, original price, discount, rating, delivery, and source.</li><li>System selects the lowest listed price as the best deal.</li><li>System stores search logs and displays collected search data after login.</li></ol>
    <h2>2.4 Data Requirements</h2><p>Product offers contain product name, category, seller, source, price, discount, rating, delivery, mode, live/mock status, and retrieval timestamp. Search logs contain query, category, result count, best price, sources, and server timestamp.</p>

    <h1 class="page-break">CHAPTER 3: DATABASE DESIGN</h1>
    <h2>3.1 Identify End Users of the System</h2><p>The primary end user is a student or shopper comparing product offers. The project evaluator or guide reviews the collected data and documentation. A future administrator can manage providers and catalog data.</p>
    <h2>3.2 Identify Entities and Attributes through ER Diagram</h2><div class="diagram"><strong>ER DIAGRAM PLACEHOLDER</strong><br />User (id, name, email, role) → SearchLog (id, query, category, mode, result_count, best_price, searched_at)<br />SearchLog contains normalized ProductOffer records (id, product_name, seller, source, price, rating, delivery, discount).</div>
    <h2>3.3 Identify All Tables, Fields, Relationships Between Tables</h2><table><tr><th>Entity</th><th>Important fields</th><th>Relationship</th></tr><tr><td>User</td><td>id, name, email, role</td><td>User views collected SearchLog records</td></tr><tr><td>SearchLog</td><td>id, query, category, mode, result_count, best_price, searched_at</td><td>One search has many source names and offer results</td></tr><tr><td>ProductOffer</td><td>id, product_name, source, seller, price, rating, delivery, discount</td><td>Offers are compared for a SearchLog query</td></tr></table>

    <h1 class="page-break">CHAPTER 4: SYSTEM DESIGN</h1>
    <p>The following UML and architecture diagrams should be inserted or drawn in the final Word submission. The labels below provide the required diagram scope for DealScout.</p>
    <h2>4.1 Class Diagram</h2><div class="diagram">Classes: User, ProductOffer, SearchLog, SearchService, AuthService, AnalyticsService.</div>
    <h2>4.2 Object Diagram</h2><div class="diagram">Objects: demoStudent, iphoneOfferAmazon, iphoneOfferFlipkart, iphoneSearchLog.</div>
    <h2>4.3 Component Diagram</h2><div class="diagram">Browser UI → FastAPI REST API → Auth / Product Search / Analytics routers → MongoDB and optional shopping provider.</div>
    <h2>4.4 Deployment Diagram</h2><div class="diagram">Student browser → Vite frontend server → FastAPI backend → MongoDB; optional provider is reached from the backend only.</div>
    <h2>4.5 Use Case Diagram</h2><div class="diagram">Actor: Student. Use cases: Login, Search Product, Select Category, Compare Offers, View Best Deal, View Collected Data, Read Documentation.</div>
    <h2>4.6 Activity Diagram</h2><div class="diagram">Enter query → Validate query → Select mode → Fetch offers → Normalize offers → Find minimum price → Display comparison → Store search log.</div>
    <h2>4.7 Sequence Diagram</h2><div class="diagram">Student submits search → UI calls /api/products/search → backend reads catalog/provider → backend saves SearchLog → JSON response returns → UI renders best deal and table.</div>

    <h1 class="page-break">CHAPTER 5: INPUT AND OUTPUT SCREEN LAYOUT</h1>
    <h2>5.1 Input Screen Layout</h2><h3>5.1.1 Login Screen</h3><p>Input fields: email and password. The demo account is used for accessing collected search data.</p><h3>5.1.2 Registration Screen</h3><p>Future scope placeholder: name, email, password, and confirmation fields can be added if registration is required by the department.</p><h3>5.1.3 Add Record Screen</h3><p>Future scope placeholder: an admin can add product name, source, seller, price, rating, delivery, and discount to the demo catalog.</p>
    <h2>5.2 Output Screen Layout</h2><h3>5.2.1 Dashboard</h3><p>DealScout dashboard contains navigation, mode switcher, category selector, search form, and academic documentation link.</p><h3>5.2.2 Search Result Screen</h3><p>The result screen contains the best-deal banner and a comparison table for seller, price, rating, delivery, discount, and action.</p><h3>5.2.3 Report Screen</h3><p>The collected-data screen contains total searches, unique queries, top query, recent searches, and source frequency.</p><p><strong>Screenshot insertion note:</strong> Add screenshots of the Login, Dashboard, Search Result, and Collected Data screens from the running DealScout preview before final submission.</p>

    <h1 class="page-break">CHAPTER 6: BIBLIOGRAPHY / REFERENCES</h1>
    <ol><li>FastAPI Documentation, https://fastapi.tiangolo.com/</li><li>React Documentation, https://react.dev/</li><li>MongoDB Documentation, https://www.mongodb.com/docs/</li><li>SerpApi Google Shopping API Documentation, https://serpapi.com/google-shopping-api</li><li>MDN Web Docs: HTML, CSS, JavaScript and Fetch API, https://developer.mozilla.org/</li><li>Savitribai Phule Pune University project and course guidelines supplied by Kaveri College of Arts, Science &amp; Commerce.</li></ol>
    <p class="footer-note">Prepared for TYBSC(CS) (SEM – V), Academic Year 2026–27. Review and update placeholders with student, guide, seat number, diagrams, screenshots, and final page numbers before submission.</p>
  </section>
</body>
</html>`;

export function downloadProjectReport() {
  const blob = new Blob([reportHtml], { type: "application/msword" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "DealScout_Project_Report.doc";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}