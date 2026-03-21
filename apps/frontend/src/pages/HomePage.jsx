import { PageContainer } from "../components/common/PageContainer";
import { SectionTitle } from "../components/common/SectionTitle";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";

export default function HomePage() {
  return (
    <PageContainer>
      <SectionTitle
        title="Frontend Zeus preparado"
        subtitle="Ambiente base pronto para receber páginas reais no futuro."
      />

      <Card>
        <CardHeader>
          <CardTitle>Status da estrutura</CardTitle>
          <CardDescription>
            Rotas, componentes reutilizáveis e padrão de API já preparados.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-600">
            Esta página é mockada e existe apenas para validar a estrutura inicial.
          </p>
        </CardContent>
      </Card>
    </PageContainer>
  );
}