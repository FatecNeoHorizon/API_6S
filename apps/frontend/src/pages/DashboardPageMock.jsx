import { PageContainer } from "../components/common/pageContainer";
import { SectionTitle } from "../components/common/SectionTitle";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function DashboardPageMock() {
  return (
    <PageContainer>
      <SectionTitle
        title="Dashboard"
        subtitle="Exemplo visual alinhado à base do frontend futuro."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Card 1</CardTitle>
          </CardHeader>
          <CardContent>Conteúdo mockado</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Card 2</CardTitle>
          </CardHeader>
          <CardContent>Conteúdo mockado</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Card 3</CardTitle>
          </CardHeader>
          <CardContent>Conteúdo mockado</CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}