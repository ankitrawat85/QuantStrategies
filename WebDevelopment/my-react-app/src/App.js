import "./style.css";
//import { initialFacts } from "./data.js";
import initialFacts from "./data.js";

function App() {
  const appTitle = "Today I Learned";

  return (
    <>
      <header className="header">
        <div className="logo">
          <img
            src="logo.png"
            height="68"
            width="68"
            alt="Today I Learned Logo"
          />
          <h1>{appTitle}</h1>
        </div>

        <button className="btn btn-large btn-open">Share a Fact</button>
      </header>

      <NewFactForm />

      <main className="main">
        <CategoryFilter />
        <FactList />
      </main>
    </>
  );
}

function NewFactForm() {
  return <form> Fact Form </form>;
}

function FactList() {
  const facts = initialFacts;
  return (
    <section>
      <ul className="facts-list">
        {facts.map((fact) => (
          <li>
            <p>{fact.text}</p>
            <div className="vote button">
              <button> {fact.votesInteresting} </button>
              <button> {fact.votesFalse} </button>
              <button> {fact.votesMindblowing} </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function CategoryFilter() {
  return <aside> Catrogry Filter </aside>;
}

export default App;
