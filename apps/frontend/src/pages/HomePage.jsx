import { Link } from "react-router-dom";

import { PageContainer } from "@/components/common/PageContainer";
import { SectionTitle } from "@/components/common/SectionTitle";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <PageContainer>
      <SectionTitle
        title="Frontend Setup Completed"
        subtitle="Use the links below to navigate through the application pages."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        
        {/* Login */}
        <Card>
          <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>Access the login page</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/login">
              <Button className="w-full">Go to Login</Button>
            </Link>
          </CardContent>
        </Card>

        {/* First Access */}
        <Card>
          <CardHeader>
            <CardTitle>First Access</CardTitle>
            <CardDescription>Set your password</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/primeiro-acesso">
              <Button variant="secondary" className="w-full">
                Go to First Access
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Dashboard */}
        <Card>
          <CardHeader>
            <CardTitle>Dashboard</CardTitle>
            <CardDescription>Main application area</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/dashboard">
              <Button variant="outline" className="w-full">
                Go to Dashboard
              </Button>
            </Link>
          </CardContent>
        </Card>

      </div>
    </PageContainer>
  );
}