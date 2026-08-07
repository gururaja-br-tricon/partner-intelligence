import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

PARTNER_DOCUMENTS = {
    "P001": {
        "name": "Nexora Technologies",
        "overview": (
            "Nexora Technologies is an information technology services "
            "company headquartered in Austin, Texas. Founded in 2008, "
            "the company focuses on helping mid-market and enterprise "
            "organizations modernize their technology environments."
        ),
        "business_focus": (
            "Nexora focuses on cloud transformation, artificial "
            "intelligence adoption, cybersecurity and application "
            "modernization. The company combines consulting, implementation "
            "and managed services to support organizations through "
            "technology modernization programs."
        ),
        "industries_served": (
            "Nexora primarily serves financial services, healthcare, "
            "retail, manufacturing and professional services organizations. "
            "Its services are particularly relevant to companies with "
            "complex technology environments and significant modernization "
            "requirements."
        ),
        "geographic_presence": (
            "Nexora is headquartered in Austin, Texas and primarily serves "
            "customers across North America. The company supports both "
            "regional and enterprise customers through distributed delivery "
            "teams."
        ),
        "capabilities": (
            "Nexora has strong capabilities in artificial intelligence, "
            "cloud services, cybersecurity, DevOps and application "
            "modernization. The company has particular experience in "
            "enterprise cloud adoption and modernization of legacy "
            "applications."
        ),
        "technology_expertise": (
            "The company's technology expertise includes cloud platforms, "
            "AI and machine learning solutions, DevOps practices, "
            "application modernization and enterprise cybersecurity. "
            "Nexora works across both Microsoft and AWS ecosystems."
        ),
        "services_offered": (
            "Nexora offers cloud migration, cloud modernization, AI "
            "implementation, cybersecurity assessments, DevOps enablement "
            "and application modernization services."
        ),
        "ecosystem": (
            "Nexora participates in Microsoft, AWS and Cisco partner "
            "programs. Its multi-vendor ecosystem allows the company "
            "to support customers operating across different technology "
            "platforms."
        ),
        "certifications": (
            "Nexora maintains a team of technology professionals with "
            "certifications and practical experience across cloud, "
            "cybersecurity and AI-related technologies."
        ),
        "customer_profile": (
            "The company's typical customers are mid-market and enterprise "
            "organizations that need to modernize infrastructure, migrate "
            "applications to the cloud or introduce AI capabilities."
        ),
        "strengths": (
            "Nexora's strongest areas are the combination of AI, cloud "
            "transformation and cybersecurity. This combination allows "
            "the company to address both modernization and security "
            "requirements within the same engagement."
        ),
        "differentiators": (
            "Nexora differentiates itself by combining transformation "
            "consulting with managed technology services. Customers can "
            "engage the company for strategy, implementation and ongoing "
            "operational support."
        ),
        "recent_initiatives": (
            "The company has been expanding its generative AI advisory "
            "services and increasing its focus on cloud modernization "
            "programs."
        ),
        "strategic_focus": (
            "Nexora's strategic focus areas include generative AI adoption, "
            "cloud modernization, zero-trust security and enterprise "
            "application modernization."
        ),
        "summary": (
            "Nexora Technologies is a technology services partner with "
            "strong AI, cloud and cybersecurity capabilities. Its broad "
            "technology ecosystem and enterprise modernization experience "
            "make it suitable for organizations pursuing large-scale "
            "technology transformation."
        ),
    },
    "P002": {
        "name": "CloudBridge Solutions",
        "overview": (
            "CloudBridge Solutions is a cloud services provider "
            "headquartered in San Francisco, California. Founded in 2012, "
            "the company helps organizations migrate applications and "
            "infrastructure to public cloud platforms."
        ),
        "business_focus": (
            "CloudBridge focuses primarily on cloud migration, cloud "
            "architecture, DevOps and application modernization. Its "
            "services are designed to help organizations accelerate "
            "cloud adoption while improving operational efficiency."
        ),
        "industries_served": (
            "CloudBridge primarily serves software companies, financial "
            "services organizations, retail companies and technology-driven "
            "businesses."
        ),
        "geographic_presence": (
            "The company is headquartered in San Francisco and primarily "
            "serves customers across the United States."
        ),
        "capabilities": (
            "CloudBridge specializes in cloud, artificial intelligence, "
            "DevOps and application modernization. Cloud architecture "
            "and migration are among its strongest capabilities."
        ),
        "technology_expertise": (
            "The company has expertise in public cloud architectures, "
            "cloud-native application development, DevOps automation and "
            "modern application platforms."
        ),
        "services_offered": (
            "Services include cloud migration, cloud architecture design, "
            "application modernization, DevOps implementation and cloud "
            "optimization."
        ),
        "ecosystem": (
            "CloudBridge participates in Microsoft and AWS partner "
            "programs and supports customers operating on both cloud "
            "platforms."
        ),
        "certifications": (
            "CloudBridge maintains certified cloud architects, engineers "
            "and DevOps professionals across its delivery organization."
        ),
        "customer_profile": (
            "Its typical customers are organizations moving workloads "
            "from traditional infrastructure to public cloud platforms "
            "or modernizing existing cloud environments."
        ),
        "strengths": (
            "Cloud migration, cloud architecture and DevOps are the "
            "company's primary strengths."
        ),
        "differentiators": (
            "CloudBridge differentiates itself through a cloud-first "
            "delivery approach and strong focus on automation."
        ),
        "recent_initiatives": (
            "The company has increased its focus on cloud-native "
            "application modernization and AI-enabled cloud workloads."
        ),
        "strategic_focus": (
            "Its strategic priorities include cloud modernization, "
            "DevOps automation and AI-enabled application development."
        ),
        "summary": (
            "CloudBridge Solutions is a cloud-focused partner with strong "
            "AWS and Microsoft ecosystem participation and expertise in "
            "cloud migration, DevOps and application modernization."
        ),
    },
    "P003": {
        "name": "Vertex Digital Systems",
        "overview": (
            "Vertex Digital Systems is a digital transformation company "
            "headquartered in Munich, Germany. Founded in 2005, the company "
            "works with large organizations on complex technology "
            "transformation initiatives."
        ),
        "business_focus": (
            "Vertex focuses on artificial intelligence, data and analytics, "
            "cloud transformation and enterprise digital transformation."
        ),
        "industries_served": (
            "The company primarily serves manufacturing, automotive, "
            "financial services, healthcare and large enterprise customers."
        ),
        "geographic_presence": (
            "Vertex is headquartered in Munich and serves customers "
            "primarily across Germany and wider European markets."
        ),
        "capabilities": (
            "Vertex has expert capabilities in AI, data and analytics, "
            "digital transformation, cloud and application modernization."
        ),
        "technology_expertise": (
            "Its technology expertise includes AI platforms, advanced "
            "analytics, cloud architectures, data engineering and "
            "enterprise application modernization."
        ),
        "services_offered": (
            "Services include AI strategy and implementation, data "
            "analytics, cloud transformation, application modernization "
            "and digital strategy consulting."
        ),
        "ecosystem": (
            "Vertex participates in Microsoft, AWS and Google Cloud "
            "partner ecosystems."
        ),
        "certifications": (
            "The company maintains experienced teams across AI, cloud, "
            "data engineering and enterprise architecture."
        ),
        "customer_profile": (
            "Vertex typically works with large enterprises that have "
            "complex data environments and multi-year digital "
            "transformation programs."
        ),
        "strengths": (
            "AI, advanced analytics and enterprise digital transformation "
            "are Vertex's strongest areas."
        ),
        "differentiators": (
            "Vertex combines data expertise with AI and broader "
            "enterprise transformation capabilities."
        ),
        "recent_initiatives": (
            "The company has expanded its AI and advanced analytics "
            "services, particularly for enterprise data modernization."
        ),
        "strategic_focus": (
            "Vertex is focused on enterprise AI adoption, data "
            "modernization and large-scale digital transformation."
        ),
        "summary": (
            "Vertex Digital Systems is an enterprise-focused digital "
            "transformation partner with particularly strong AI, data "
            "and analytics capabilities."
        ),
    },
    "P004": {
        "name": "BluePeak IT Services",
        "overview": (
            "BluePeak IT Services is a managed services provider "
            "headquartered in Dallas, Texas. The company provides "
            "ongoing technology operations and security services."
        ),
        "business_focus": (
            "BluePeak focuses on managed IT services, cybersecurity, "
            "cloud infrastructure and networking."
        ),
        "industries_served": (
            "The company primarily serves healthcare, professional "
            "services, retail and mid-market businesses."
        ),
        "geographic_presence": (
            "BluePeak is headquartered in Dallas and primarily serves "
            "customers across the United States."
        ),
        "capabilities": (
            "BluePeak has expert cybersecurity and managed services "
            "capabilities along with advanced cloud and networking "
            "expertise."
        ),
        "technology_expertise": (
            "The company specializes in security operations, cloud "
            "infrastructure, networking and managed IT environments."
        ),
        "services_offered": (
            "Services include managed IT operations, cybersecurity "
            "monitoring, cloud infrastructure management and network "
            "management."
        ),
        "ecosystem": ("BluePeak participates in Microsoft and Cisco partner programs."),
        "certifications": (
            "BluePeak maintains certified professionals across "
            "cybersecurity, networking and cloud technologies."
        ),
        "customer_profile": (
            "Its typical customers are mid-market organizations that "
            "need outsourced IT operations and stronger cybersecurity "
            "capabilities."
        ),
        "strengths": (
            "Cybersecurity and managed services are BluePeak's primary " "strengths."
        ),
        "differentiators": (
            "BluePeak combines managed IT operations with dedicated "
            "cybersecurity capabilities."
        ),
        "recent_initiatives": (
            "The company has increased its focus on managed security "
            "services and cloud security."
        ),
        "strategic_focus": (
            "Its strategic focus includes cybersecurity, managed cloud "
            "services and network modernization."
        ),
        "summary": (
            "BluePeak IT Services is a managed services partner with "
            "strong cybersecurity and infrastructure capabilities."
        ),
    },
    "P005": {
        "name": "ApexSphere Consulting",
        "overview": (
            "ApexSphere Consulting is an IT consulting and systems "
            "integration company headquartered in Bangalore, India."
        ),
        "business_focus": (
            "ApexSphere focuses on AI consulting, cloud transformation, "
            "data analytics and digital strategy."
        ),
        "industries_served": (
            "The company serves financial services, retail, healthcare, "
            "technology and manufacturing organizations."
        ),
        "geographic_presence": (
            "ApexSphere is headquartered in Bangalore and provides "
            "technology services across India and international markets."
        ),
        "capabilities": (
            "The company has advanced capabilities in AI, cloud, data "
            "analytics and DevOps, with expert-level digital "
            "transformation expertise."
        ),
        "technology_expertise": (
            "ApexSphere specializes in AI implementation, cloud "
            "architecture, data engineering, analytics and DevOps."
        ),
        "services_offered": (
            "Services include AI consulting, cloud migration, data "
            "analytics, digital transformation and DevOps implementation."
        ),
        "ecosystem": (
            "ApexSphere participates in Microsoft, AWS and Google Cloud "
            "partner programs."
        ),
        "certifications": (
            "The company maintains certified professionals across cloud, "
            "AI, data and DevOps technologies."
        ),
        "customer_profile": (
            "ApexSphere typically works with organizations beginning "
            "AI or cloud transformation programs."
        ),
        "strengths": (
            "AI consulting, cloud transformation and digital strategy "
            "are the company's strongest areas."
        ),
        "differentiators": (
            "ApexSphere combines consulting expertise with hands-on "
            "implementation capabilities."
        ),
        "recent_initiatives": (
            "The company has expanded its AI advisory and generative "
            "AI implementation services."
        ),
        "strategic_focus": (
            "Its strategic focus includes enterprise AI adoption, "
            "cloud transformation and data modernization."
        ),
        "summary": (
            "ApexSphere Consulting is an India-based systems integration "
            "and consulting partner with strong AI, cloud and data "
            "transformation capabilities."
        ),
    },
    "P006": {
        "name": "Crestview Technology Group",
        "overview": (
            "Crestview Technology Group is a technology infrastructure "
            "and networking provider headquartered in London."
        ),
        "business_focus": (
            "Crestview focuses on enterprise networking, infrastructure "
            "modernization and network security."
        ),
        "industries_served": (
            "The company serves financial services, telecommunications, "
            "manufacturing and large enterprise organizations."
        ),
        "geographic_presence": (
            "Crestview is headquartered in London and primarily serves "
            "customers across the United Kingdom and Europe."
        ),
        "capabilities": (
            "The company has expert capabilities in networking and "
            "infrastructure along with advanced cybersecurity and cloud "
            "capabilities."
        ),
        "technology_expertise": (
            "Crestview specializes in enterprise networking, infrastructure "
            "architecture, network security and cloud connectivity."
        ),
        "services_offered": (
            "Services include network architecture, infrastructure "
            "modernization, network security and cloud connectivity."
        ),
        "ecosystem": (
            "Crestview participates in Cisco and Microsoft partner programs."
        ),
        "certifications": (
            "The company maintains experienced networking and "
            "infrastructure professionals with industry certifications."
        ),
        "customer_profile": (
            "Its customers are typically large organizations with "
            "complex networking and infrastructure requirements."
        ),
        "strengths": (
            "Enterprise networking and infrastructure are Crestview's "
            "primary strengths."
        ),
        "differentiators": (
            "Crestview combines traditional infrastructure expertise "
            "with modern cloud connectivity."
        ),
        "recent_initiatives": (
            "The company has increased its focus on hybrid cloud "
            "networking and infrastructure modernization."
        ),
        "strategic_focus": (
            "Its strategic priorities include network modernization, "
            "hybrid cloud connectivity and security."
        ),
        "summary": (
            "Crestview Technology Group is an infrastructure-focused "
            "partner with particularly strong networking capabilities."
        ),
    },
    "P007": {
        "name": "NorthStar Managed Services",
        "overview": (
            "NorthStar Managed Services is a Canadian managed services "
            "provider headquartered in Toronto."
        ),
        "business_focus": (
            "NorthStar focuses on managed cloud services, cybersecurity "
            "and infrastructure operations."
        ),
        "industries_served": (
            "The company serves financial services, healthcare, retail "
            "and professional services organizations."
        ),
        "geographic_presence": (
            "NorthStar is headquartered in Toronto and primarily serves "
            "customers across Canada and North America."
        ),
        "capabilities": (
            "NorthStar has expert capabilities in managed services and "
            "cloud, with advanced cybersecurity, infrastructure and "
            "DevOps expertise."
        ),
        "technology_expertise": (
            "The company specializes in managed cloud infrastructure, "
            "security operations, infrastructure management and DevOps."
        ),
        "services_offered": (
            "Services include managed cloud operations, infrastructure "
            "management, cybersecurity monitoring and DevOps support."
        ),
        "ecosystem": (
            "NorthStar participates in AWS, Microsoft and Cisco partner " "programs."
        ),
        "certifications": (
            "NorthStar maintains certified cloud, infrastructure and "
            "security professionals."
        ),
        "customer_profile": (
            "Its typical customers are organizations that want to "
            "outsource infrastructure and cloud operations while "
            "maintaining strong security controls."
        ),
        "strengths": (
            "Managed cloud services and cybersecurity are its primary " "strengths."
        ),
        "differentiators": (
            "NorthStar differentiates itself through its combination "
            "of managed operations and cloud expertise."
        ),
        "recent_initiatives": (
            "The company has expanded its managed security and cloud "
            "optimization offerings."
        ),
        "strategic_focus": (
            "Its strategic focus includes managed cloud, security "
            "operations and infrastructure automation."
        ),
        "summary": (
            "NorthStar Managed Services is a Canadian MSP with strong "
            "cloud, cybersecurity and infrastructure capabilities."
        ),
    },
    "P008": {
        "name": "QuantumEdge Solutions",
        "overview": (
            "QuantumEdge Solutions is an Australian data and analytics "
            "technology company headquartered in Sydney."
        ),
        "business_focus": (
            "QuantumEdge focuses on artificial intelligence, advanced "
            "analytics, cloud data platforms and digital transformation."
        ),
        "industries_served": (
            "The company serves financial services, retail, healthcare "
            "and technology organizations."
        ),
        "geographic_presence": (
            "QuantumEdge is headquartered in Sydney and primarily serves "
            "customers across Australia and the Asia-Pacific region."
        ),
        "capabilities": (
            "The company has expert capabilities in AI and data analytics "
            "along with advanced cloud and digital transformation "
            "capabilities."
        ),
        "technology_expertise": (
            "QuantumEdge specializes in machine learning, analytics, "
            "cloud data platforms and data-driven transformation."
        ),
        "services_offered": (
            "Services include AI implementation, analytics platforms, "
            "data engineering and cloud data modernization."
        ),
        "ecosystem": (
            "QuantumEdge participates in AWS, Google Cloud and Microsoft "
            "partner programs."
        ),
        "certifications": (
            "The company maintains certified data, cloud and AI " "professionals."
        ),
        "customer_profile": (
            "QuantumEdge typically works with organizations that want "
            "to use data and AI to improve decision-making and "
            "operational processes."
        ),
        "strengths": ("AI and advanced analytics are QuantumEdge's strongest areas."),
        "differentiators": (
            "QuantumEdge combines data engineering with AI implementation "
            "and cloud expertise."
        ),
        "recent_initiatives": (
            "The company has expanded its generative AI and predictive "
            "analytics offerings."
        ),
        "strategic_focus": (
            "Its strategic priorities include AI adoption, advanced "
            "analytics and cloud data modernization."
        ),
        "summary": (
            "QuantumEdge Solutions is a data and AI-focused technology "
            "partner with strong analytics and cloud capabilities."
        ),
    },
    "P009": {
        "name": "Silverline Systems",
        "overview": (
            "Silverline Systems is an enterprise technology provider "
            "based in Mumbai, India."
        ),
        "business_focus": (
            "Silverline focuses on infrastructure, networking, cloud "
            "and cybersecurity services."
        ),
        "industries_served": (
            "The company serves banking, manufacturing, retail and "
            "enterprise technology organizations."
        ),
        "geographic_presence": (
            "Silverline is headquartered in Mumbai and serves customers "
            "across India."
        ),
        "capabilities": (
            "Silverline has advanced capabilities in infrastructure, "
            "networking, cloud and cybersecurity."
        ),
        "technology_expertise": (
            "The company specializes in enterprise infrastructure, "
            "network architecture, cloud connectivity and security."
        ),
        "services_offered": (
            "Services include infrastructure deployment, network "
            "modernization, cloud infrastructure and cybersecurity."
        ),
        "ecosystem": (
            "Silverline participates in Microsoft and Cisco partner " "programs."
        ),
        "certifications": (
            "The company maintains certified networking, infrastructure "
            "and cybersecurity professionals."
        ),
        "customer_profile": (
            "Its customers are typically mid-market and enterprise "
            "organizations with infrastructure modernization needs."
        ),
        "strengths": (
            "Infrastructure and enterprise networking are Silverline's "
            "primary strengths."
        ),
        "differentiators": (
            "Silverline combines infrastructure expertise with cloud "
            "and cybersecurity capabilities."
        ),
        "recent_initiatives": (
            "The company has increased its focus on hybrid cloud "
            "infrastructure and security modernization."
        ),
        "strategic_focus": (
            "Its strategic focus includes infrastructure modernization, "
            "cloud adoption and cybersecurity."
        ),
        "summary": (
            "Silverline Systems is an India-based enterprise technology "
            "provider with strong infrastructure, networking and "
            "cybersecurity capabilities."
        ),
    },
    "P010": {
        "name": "BrightPath Digital",
        "overview": (
            "BrightPath Digital is a cybersecurity-focused managed "
            "services provider headquartered in Berlin, Germany."
        ),
        "business_focus": (
            "BrightPath focuses on cybersecurity, secure cloud "
            "transformation and managed security services."
        ),
        "industries_served": (
            "The company primarily serves financial services, healthcare, "
            "manufacturing and professional services organizations."
        ),
        "geographic_presence": (
            "BrightPath is headquartered in Berlin and primarily serves "
            "customers across Germany and European markets."
        ),
        "capabilities": (
            "BrightPath has expert cybersecurity capabilities along with "
            "advanced cloud, DevOps and application modernization "
            "capabilities."
        ),
        "technology_expertise": (
            "The company specializes in security operations, cloud "
            "security, secure application modernization and DevSecOps."
        ),
        "services_offered": (
            "Services include managed security, security assessments, "
            "cloud security, DevSecOps and application modernization."
        ),
        "ecosystem": (
            "BrightPath participates in Microsoft and AWS partner " "programs."
        ),
        "certifications": (
            "The company maintains certified cybersecurity and cloud " "professionals."
        ),
        "customer_profile": (
            "BrightPath typically works with organizations that have "
            "strict security requirements or are modernizing their "
            "technology environments."
        ),
        "strengths": (
            "Cybersecurity and secure cloud transformation are the "
            "company's primary strengths."
        ),
        "differentiators": (
            "BrightPath combines managed security operations with "
            "cloud modernization capabilities."
        ),
        "recent_initiatives": (
            "The company has expanded its DevSecOps and cloud security " "offerings."
        ),
        "strategic_focus": (
            "Its strategic focus includes zero-trust security, "
            "cloud security and secure application modernization."
        ),
        "summary": (
            "BrightPath Digital is a cybersecurity-focused MSP with "
            "strong expertise in cloud security, DevSecOps and secure "
            "application modernization."
        ),
    },
}


def generate_documents(output_dir):
    documents_dir = os.path.join(output_dir, "documents")

    os.makedirs(documents_dir, exist_ok=True)

    styles = getSampleStyleSheet()

    for partner_id, data in PARTNER_DOCUMENTS.items():
        file_path = os.path.join(documents_dir, f"{partner_id}.pdf")

        document = SimpleDocTemplate(file_path, pagesize=letter)

        content = []

        content.append(Paragraph(data["name"], styles["Title"]))

        content.append(Spacer(1, 12))

        sections = [
            ("Company Overview", data["overview"]),
            ("Business Focus", data["business_focus"]),
            ("Industries Served", data["industries_served"]),
            ("Geographic Presence", data["geographic_presence"]),
            ("Core Capabilities", data["capabilities"]),
            ("Technology Expertise", data["technology_expertise"]),
            ("Services Offered", data["services_offered"]),
            ("Partner Ecosystem", data["ecosystem"]),
            ("Certifications & Expertise", data["certifications"]),
            ("Typical Customer Profile", data["customer_profile"]),
            ("Key Strengths", data["strengths"]),
            ("Differentiators", data["differentiators"]),
            ("Recent Initiatives", data["recent_initiatives"]),
            ("Strategic Focus", data["strategic_focus"]),
            ("Summary", data["summary"]),
        ]

        for title, text in sections:
            content.append(Paragraph(title, styles["Heading2"]))

            content.append(Paragraph(text, styles["BodyText"]))
            content.append(Spacer(1, 10))

        document.build(content)

        print(f"Generated document: {file_path}")
