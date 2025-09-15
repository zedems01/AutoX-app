"use client"

import { useMutation } from "@tanstack/react-query"
import { useRouter, useSearchParams } from "next/navigation"
import { toast } from "sonner"
import { Loader2, ShieldCheck, ShieldX } from "lucide-react"
import { Suspense, useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { demoLogin } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

function DemoLogin() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login: authLogin } = useAuth()
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const tokenFromUrl = searchParams.get("token")
    if (tokenFromUrl) {
      setToken(tokenFromUrl)
    }
  }, [searchParams])

  const mutation = useMutation({
    mutationFn: (token: string) => demoLogin(token),
    onSuccess: data => {
      toast.success("Login successful!", { duration: 5000 })
      authLogin(data)
      router.push("/")
    },
    onError: error => {
      toast.error(`Demo login failed: ${error.message}`, {
        duration: 15000,
      })
    },
  })

  function handleDemoLogin() {
    if (token) {
      mutation.mutate(token)
    }
  }

  if (!token) {
    return (
      <div className="flex justify-center items-start min-h-screen px-4 py-6 md:py-12">
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center pb-4 md:pb-6 px-4 md:px-6">
            <div className="mx-auto bg-destructive/10 w-fit p-2 md:p-3 rounded-lg mb-3 md:mb-4">
              <ShieldX className="h-8 w-8 md:h-10 md:w-10 text-destructive" />
            </div>
            <CardTitle className="text-lg md:text-xl">Access Denied</CardTitle>
            <CardDescription className="text-sm md:text-base">
              This demo link is invalid or incomplete. Please use the link
              provided by the administrator.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex justify-center items-start min-h-screen px-4 py-6 md:py-12">
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center pb-4 md:pb-6 px-4 md:px-6">
          <div className="mx-auto bg-primary/10 w-fit p-2 md:p-3 rounded-lg mb-3 md:mb-4">
            <ShieldCheck className="h-8 w-8 md:h-10 md:w-10 text-primary" />
          </div>
          <CardTitle className="text-lg md:text-xl">AutoX Workflow Demo</CardTitle>
          <CardDescription className="text-sm md:text-base">
            Click the button below to log in with a demo account and try out the
            workflow.
          </CardDescription>
        </CardHeader>
        <CardContent className="px-4 md:px-6 pb-6">
          <Button
            onClick={handleDemoLogin}
            className="w-full cursor-pointer h-10 md:h-11 text-sm md:text-base font-medium"
            disabled={mutation.isPending || !token}
          >
            {mutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Access Demo
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default function DemoLoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DemoLogin />
    </Suspense>
  )
}
