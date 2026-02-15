export interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

export interface MockAIResponse {
  response: string;
  context_chunks: SourceChunk[];
}

export const generateMockAIResponse = (query: string): MockAIResponse => {
  return {
    response: `
# Comprehensive Overview of the Education Policy

## 1. Executive Summary

The Education Policy establishes a structured reform framework aimed at improving access, quality, equity, and institutional accountability across the education ecosystem. It transitions the system from a compliance-driven model to a learner-centric, outcome-based framework supported by digital integration and regulatory transparency.

The policy applies across primary, secondary, and higher education institutions, with differentiated implementation pathways at central and state levels.

---

## 2. Policy Vision and Guiding Principles

The policy is built around five core principles:

- **Access and Inclusion** – Ensuring equitable participation across socio-economic groups.
- **Quality and Learning Outcomes** – Shifting focus from rote assessment to competency-based evaluation.
- **Flexibility and Choice** – Allowing multidisciplinary pathways and modular curriculum design.
- **Digital Integration** – Embedding technology into teaching, governance, and assessment.
- **Institutional Accountability** – Strengthening accreditation, disclosure norms, and performance metrics.

---

## 3. Structural Reforms

### 3.1 Curriculum and Pedagogy Reform

The policy promotes:

- Competency-based learning frameworks  
- Multidisciplinary subject combinations  
- Reduction in content overload  
- Experiential and skill-based modules  

Assessment reforms include a move away from high-stakes board examinations toward modular, periodic evaluation mechanisms.

---

### 3.2 Governance and Regulatory Architecture

The governance framework is reorganized into clearly defined verticals:

1. **Policy Formulation Bodies** – Responsible for national standards and strategic direction  
2. **Academic Councils** – Curriculum alignment and pedagogical guidance  
3. **Accreditation Authorities** – Quality assurance and institutional grading  
4. **Funding and Financial Oversight Units** – Resource allocation and compliance monitoring  

This separation reduces conflict of interest between regulation, funding, and academic operations.

---

## 4. Digital and Technological Integration

The policy integrates digital systems at three levels:

| Domain | Reform Measure | Expected Impact |
|--------|---------------|----------------|
| Teaching | Learning Management Systems | Improved accessibility |
| Assessment | Digital evaluation tools | Transparency & speed |
| Governance | Data-driven dashboards | Real-time monitoring |

Technology adoption includes blended learning models, digital repositories, and remote access mechanisms to reduce geographical disparities.

---

## 5. Equity and Inclusion Measures

Special provisions are introduced for:

- Rural and underserved populations  
- Students with disabilities  
- Economically disadvantaged groups  
- First-generation learners  

Targeted funding mechanisms and scholarship programs aim to reduce dropout rates and improve retention.

---

## 6. Implementation Strategy

Implementation is phased over multiple years and includes:

- Institutional capacity-building programs  
- Faculty training and certification modules  
- Digital infrastructure expansion  
- Monitoring through measurable Key Performance Indicators (KPIs)

Periodic review mechanisms are embedded to allow adaptive policy refinement.

---

## 7. Expected Outcomes

If executed effectively, the policy is expected to:

- Improve Gross Enrollment Ratios  
- Enhance employability and skill alignment  
- Increase institutional transparency  
- Foster innovation in pedagogy  
- Strengthen global competitiveness of institutions  

---

## 8. Conclusion

The Education Policy represents a systemic shift from input-based governance to outcome-oriented reform. Its success will depend on coordinated implementation across central and state authorities, adequate funding allocation, and sustained institutional capacity development.

The framework is comprehensive, but long-term impact will be contingent upon execution fidelity, regulatory clarity, and measurable performance tracking.
`,
    context_chunks: [
      {
        text: "The policy emphasizes competency-based learning and institutional accountability...",
        source: "Education_Reform_Framework.pdf",
        page_number: 14,
      },
      {
        text: "Digital integration is positioned as a cross-cutting reform mechanism...",
        source: "National_Digital_Education_Strategy.pdf",
        page_number: 22,
      },
    ],
  };
};
